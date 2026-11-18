import random

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.catalog import get_strategy, build_strategy

from app.wrappers.encode import EncodeWrapper
from app.wrappers.decode import DecodeWrapper
from app.wrappers.channel import ChannelWrapper
from app.wrappers.protection import ProtectionWrapper

router = APIRouter(
    prefix="/communication",
    tags=["Communication"]
)

MAX_MESSAGE_LENGTH = 64
REPLICATION_FACTOR = 3


class TransmissionRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)
    error_rate: float = Field(0.05, ge=0, le=1)
    use_protection: bool = True
    seed: int | None = None
    encoder: str = "one2one"
    decoder: str = "one2one"
    channel: str = "substitution"
    protection: str = "replication"


def text_to_bits(message: str) -> str:
    return "".join(f"{byte:08b}" for byte in message.encode("utf-8"))


def bits_to_text(bits: str) -> str:
    if len(bits) % 8 != 0:
        raise ValueError("Le nombre de bits doit être un multiple de 8.")

    data = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
    return data.decode("utf-8", errors="replace")


@router.post("/encode")
def encode_message(data: str):
    """Encodage uniquement (bits -> ADN)."""
    try:
        wrapper = EncodeWrapper(get_strategy("encoder", "one2one")())
        encoded = wrapper.encode(data)

        return {"message": "Encodage effectué", "data": data, "encoded": encoded}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/run")
def run_transmission(request: TransmissionRequest):
    """Exécution de la chaîne de transmission complète.

    Les implémentations utilisées à chaque étape proviennent du registre
    `app/catalog.py` (sélectionnables via les champs encoder / decoder /
    channel / protection). Chaque étape retourne ses données d'entrée /
    sortie, décrites par les métadonnées des implémentations, afin de
    permettre la visualisation détaillée côté interface.
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide.")

    seed = request.seed if request.seed is not None else random.randrange(2 ** 32)
    apply_protection = request.use_protection

    try:
        encoder_cls = get_strategy("encoder", request.encoder)
        decoder_cls = get_strategy("decoder", request.decoder)
        channel_cls = get_strategy("channel", request.channel)
        protection_cls = get_strategy("protection", request.protection)

        steps = []

        # Étape 1 : conversion du message texte en bits (UTF-8)
        message = request.message
        bits = text_to_bits(message)
        steps.append({
            "id": "source",
            "label": "Message source",
            "description": "Texte à stocker dans l'ADN.",
            "kind": "text",
            "input_kind": "text",
            "output_kind": "text",
            "input": message,
            "output": message,
        })
        steps.append({
            "id": "bits",
            "label": "Conversion binaire",
            "description": "Le texte est converti en suite de bits (encodage UTF-8, 8 bits par caractère).",
            "kind": "bits",
            "input_kind": "text",
            "output_kind": "bits",
            "input": message,
            "output": bits,
        })

        # Étape 2 : encodage binaire -> ADN
        encoder = build_strategy("encoder", request.encoder, seed=seed)
        dna = EncodeWrapper(encoder).encode(bits)
        steps.append({
            "id": "encode",
            "label": "Encodage",
            "description": encoder.description,
            "kind": "dna",
            "input_kind": "bits",
            "output_kind": "dna",
            "strategy": encoder.slug,
            "input": bits,
            "output": dna,
        })

        # Étape 3 (optionnelle) : protection
        if apply_protection:
            protection = build_strategy(
                "protection", request.protection, factor=REPLICATION_FACTOR
            )
            protected = ProtectionWrapper(protection).protect(dna)
            steps.append({
                "id": "protect",
                "label": "Protection",
                "description": protection.description,
                "kind": "dna",
                "input_kind": "dna",
                "output_kind": "dna",
                "strategy": protection.slug,
                "input": dna,
                "output": protected,
            })
        else:
            protected = dna

        # Étape 4 : transmission dans le canal
        canal = build_strategy("channel", request.channel, error_rate=request.error_rate, seed=seed)
        channel_result = ChannelWrapper(canal).transmit(protected)
        received = channel_result["output"]
        steps.append({
            "id": "channel",
            "label": "Canal de transmission",
            "description": f"{canal.description} Taux d'erreur : {request.error_rate:.0%}.",
            "kind": "dna",
            "input_kind": "dna",
            "output_kind": "dna",
            "strategy": canal.slug,
            "error_rate": request.error_rate,
            "input": protected,
            "output": received,
            "errors": channel_result["errors"],
        })

        # Étape 5 (si protection) : restauration
        if apply_protection:
            restore_result = ProtectionWrapper(
                build_strategy("protection", request.protection, factor=REPLICATION_FACTOR)
            ).restore(received)
            restored = restore_result["output"]
            steps.append({
                "id": "restore",
                "label": "Restauration",
                "description": protection_cls.description,
                "kind": "dna",
                "input_kind": "dna",
                "output_kind": "dna",
                "strategy": protection_cls.slug,
                "input": received,
                "output": restored,
                "corrections": restore_result["corrections"],
            })
        else:
            restored = received

        # Étape 6 : décodage ADN -> bits
        decoded_bits = DecodeWrapper(decoder_cls()).decode(restored)
        steps.append({
            "id": "decode",
            "label": "Décodage",
            "description": decoder_cls.description,
            "kind": "bits",
            "input_kind": "dna",
            "output_kind": "bits",
            "strategy": decoder_cls.slug,
            "input": restored,
            "output": decoded_bits,
        })

        # Étape 7 : conversion des bits en texte
        received_message = bits_to_text(decoded_bits)
        steps.append({
            "id": "result",
            "label": "Message reçu",
            "description": "Les bits décodés sont reconvertis en texte (UTF-8).",
            "kind": "text",
            "input_kind": "bits",
            "output_kind": "text",
            "input": decoded_bits,
            "output": received_message,
        })

        errors_injected = len(channel_result["errors"])
        errors_corrected = len(restore_result["corrections"]) if apply_protection else 0

        return {
            "success": True,
            "original_message": message,
            "received_message": received_message,
            "steps": steps,
            "seed": seed,
            "stats": {
                "bits": len(bits),
                "bases_source": len(dna),
                "bases_sent": len(protected),
                "errors_injected": errors_injected,
                "errors_corrected": errors_corrected,
                "protection": apply_protection,
            },
            "integrity": message == received_message,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
