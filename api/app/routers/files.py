"""Stockage des fichiers importés encodés en ADN.

- `POST /files/import`  : import d'un fichier (multipart), encodage de son
  contenu binaire en séquence ADN via le registre des encodeurs, puis
  enregistrement en base de données.
- `GET /files`          : liste des imports déjà stockés.
- `GET /files/{id}/download` : téléchargement de la séquence ADN, relue
  depuis la base de données.

L'encodage est délégué aux implémentations concrètes (`encoders/`) : ce
router ne fait qu'orchestrer et persister.
"""
import hashlib

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import DnaFile, get_db
from app.encoders.gray_encoder import GrayEncoder
from app.encoders.one2one_encoder import One2OneEncoder
from app.protections.replication_protection import ReplicationProtection
from app.wrappers.encode import EncodeWrapper
from app.wrappers.protection import ProtectionWrapper

router = APIRouter(prefix="/files", tags=["Fichiers ADN"])

MAX_FILE_SIZE = 512 * 1024  # octets : 1 bit -> 1 base avec l'encodeur one2one
PREVIEW_BASES = 120


def _build_encoder(slug: str, seed: int | None):
    """Sélection de l'encodeur, sur le même principe que `routers/tests.py`."""
    if slug == "one2one":
        return One2OneEncoder(seed=seed)
    if slug == "gray":
        return GrayEncoder()
    raise ValueError(
        f"Encodeur '{slug}' inconnu. Choix possibles : one2one, gray."
    )


def _build_protection(slug: str):
    """Sélection du mécanisme de protection ('replication' actuellement)."""
    if slug == "replication":
        return ReplicationProtection(factor=3)
    raise ValueError(f"Mécanisme de protection '{slug}' inconnu. Choix possibles : replication.")


def _bits_from_bytes(data: bytes) -> str:
    return "".join(f"{byte:08b}" for byte in data)


@router.post("/import")
async def import_file(
    file: UploadFile,
    encoder: str = Query("one2one", description="Slug de l'encodeur (one2one, gray)."),
    protection: str = Query("", description="Mécanisme de protection ('replication') ou vide."),
    seed: int | None = Query(None, description="Graine aléatoire (reproductibilité)."),
    db: Session = Depends(get_db),
):
    """Encode le contenu du fichier en ADN et le stocke en base."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Le fichier importé doit avoir un nom.")

    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Le fichier importé est vide.")
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Fichier trop volumineux ({len(data)} octets) : maximum {MAX_FILE_SIZE} octets.",
        )

    bits = _bits_from_bytes(data)
    try:
        encoder_strategy = _build_encoder(encoder, seed)
        dna = EncodeWrapper(encoder_strategy).encode(bits)

        # Protection optionnelle : la séquence stockée est alors la version
        # protégée (redondante), comme dans la chaîne de transmission.
        stored = dna
        if protection:
            stored = ProtectionWrapper(_build_protection(protection)).protect(dna)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    record = DnaFile(
        filename=file.filename,
        sha256=hashlib.sha256(data).hexdigest(),
        byte_size=len(data),
        bit_count=len(bits),
        base_count=len(stored),
        encoder=encoder,
        seed=seed,
        sequence=stored,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "filename": record.filename,
        "byte_size": record.byte_size,
        "bit_count": record.bit_count,
        "base_count": record.base_count,
        "encoder": record.encoder,
        "protection": protection if protection else "aucune",
        "seed": record.seed,
        "sha256": record.sha256,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "preview": dna[:PREVIEW_BASES],
        "preview_truncated": len(dna) > PREVIEW_BASES,
    }


@router.get("")
def list_files(db: Session = Depends(get_db)):
    """Liste les imports ADN stockés en base (sans les séquences)."""
    records = db.execute(
        select(DnaFile).order_by(DnaFile.id.desc())
    ).scalars().all()

    return [
        {
            "id": record.id,
            "filename": record.filename,
            "byte_size": record.byte_size,
            "base_count": record.base_count,
            "encoder": record.encoder,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
        for record in records
    ]


@router.get("/{file_id}/download")
def download_dna(file_id: int, db: Session = Depends(get_db)):
    """Télécharge la séquence ADN stockée en base sous forme de fichier texte."""
    record = db.get(DnaFile, file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Fichier ADN introuvable.")

    # Nom de téléchargement sûr : séparateurs de chemins neutralisés.
    safe_name = record.filename.replace("/", "_").replace("\\", "_")

    return Response(
        content=record.sequence,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}.dna.txt"'
        },
    )
