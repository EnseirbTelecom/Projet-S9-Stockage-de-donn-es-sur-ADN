import random

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.encoders.one2one_encoder import One2OneEncoder
from app.decoders.one2one_decoder import One2OneDecoder
from app.channels.substitution_channel import SubstitutionChannel
from app.protections.replication_protection import ReplicationProtection

from app.wrappers.encode import EncodeWrapper
from app.wrappers.decode import DecodeWrapper
from app.wrappers.channel import ChannelWrapper
from app.wrappers.protection import ProtectionWrapper

router = APIRouter(
    prefix="/communication",
    tags=["Communication"]
)

MAX_MESSAGE_LENGTH = 64


class TransmissionRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)
    error_rate: float = Field(0.05, ge=0, le=1)
    use_protection: bool = True
    seed: int | None = None


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
        encoder = One2OneEncoder()
        wrapper = EncodeWrapper(encoder)
        encoded = wrapper.encode(data)

        return {"message": "Encodage effectué", "data": data, "encoded": encoded}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/run")
def run_transmission(request: TransmissionRequest):
    """Exécution de la chaîne de transmission complète.

    Chaque étape retourne ses données d'entrée / sortie afin de permettre
    la visualisation détaillée de la transmission côté interface.
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide.")

    seed = request.seed if request.seed is not None else random.randrange(2 ** 32)
    apply_protection = request.use_protection

    try:
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
        dna = EncodeWrapper(One2OneEncoder(seed=seed)).encode(bits)
        steps.append({
            "id": "encode",
            "label": "Encodage (one2one)",
            "description": "Chaque bit est converti en base : 0 -> A ou T, 1 -> C ou G.",
            "kind": "dna",
            "input_kind": "bits",
            "output_kind": "dna",
            "strategy": "one2one",
            "input": bits,
            "output": dna,
        })

        # Étape 3 (optionnelle) : protection par réplication
        if apply_protection:
            protection = ProtectionWrapper(ReplicationProtection(factor=3))
            protected = protection.protect(dna)
            steps.append({
                "id": "protect",
                "label": "Protection (réplication ×3)",
                "description": "Chaque base est répétée 3 fois afin de permettre la correction d'erreurs à la réception.",
                "kind": "dna",
                "input_kind": "dna",
                "output_kind": "dna",
                "strategy": "replication-x3",
                "input": dna,
                "output": protected,
            })
        else:
            protected = dna

        # Étape 4 : transmission dans le canal bruité
        channel_result = ChannelWrapper(
            SubstitutionChannel(error_rate=request.error_rate, seed=seed)
        ).transmit(protected)
        received = channel_result["output"]
        steps.append({
            "id": "channel",
            "label": "Canal de transmission",
            "description": f"Transmission avec un taux d'erreur de {request.error_rate:.0%} : des substitutions aléatoires de bases sont introduites.",
            "kind": "dna",
            "input_kind": "dna",
            "output_kind": "dna",
            "strategy": "substitution",
            "error_rate": request.error_rate,
            "input": protected,
            "output": received,
            "errors": channel_result["errors"],
        })

        # Étape 5 (si protection) : restauration par vote majoritaire
        if apply_protection:
            restore_result = ProtectionWrapper(ReplicationProtection(factor=3)).restore(received)
            restored = restore_result["output"]
            steps.append({
                "id": "restore",
                "label": "Restauration (vote majoritaire)",
                "description": "Pour chaque triplet répété, la base majoritaire est retenue : les substitutions isolées sont corrigées.",
                "kind": "dna",
                "input_kind": "dna",
                "output_kind": "dna",
                "strategy": "replication-x3",
                "input": received,
                "output": restored,
                "corrections": restore_result["corrections"],
            })
        else:
            restored = received

        # Étape 6 : décodage ADN -> bits
        decoded_bits = DecodeWrapper(One2OneDecoder()).decode(restored)
        steps.append({
            "id": "decode",
            "label": "Décodage (one2one)",
            "description": "Chaque base est convertie en bit : A ou T -> 0, C ou G -> 1.",
            "kind": "bits",
            "input_kind": "dna",
            "output_kind": "bits",
            "strategy": "one2one",
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
