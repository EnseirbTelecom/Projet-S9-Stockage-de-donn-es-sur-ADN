from fastapi import APIRouter, HTTPException

from app.encoders.one2one_encoder import One2OneEncoder
from app.decoders.one2one_decoder import One2OneDecoder
from app.channels.substitution_channel import SubstitutionChannel
from app.channels.canal_modele_1 import CanalModele1
from app.protections.replication_protection import ReplicationProtection

from app.wrappers.encode import EncodeWrapper
from app.wrappers.decode import DecodeWrapper
from app.wrappers.channel import ChannelWrapper
from app.wrappers.protection import ProtectionWrapper

router = APIRouter(
    prefix="/tests",
    tags=["Tests"]
)

@router.get("/encode")
def encode(data: str, strategy: str):
    try:
        if strategy == "one2one":
            encoder = One2OneEncoder()
        else:
            raise ValueError("Stratégie inconnue.")

        wrapper = EncodeWrapper(encoder)

        result = wrapper.encode(data)

        return {
            "input": data,
            "encoded": result,
            "encoder": strategy
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/decode")
def decode(sequence: str, strategy: str):
    try:
        if strategy == "one2one":
            decoder = One2OneDecoder()
        else:
            raise ValueError("Stratégie inconnue.")

        wrapper = DecodeWrapper(decoder)

        result = wrapper.decode(sequence)

        return {
            "input": sequence,
            "decoded": result,
            "decoder": strategy
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/channel")
def channel(sequence: str, error_rate: float = 0.05, strategy: str ="", pts: float = 0.1, pi: float = 0.1, pd: float = 0.1,seed: int | None = None):
    try:
        if strategy == "substitution":
            canal = SubstitutionChannel(error_rate=error_rate, seed=seed)
        elif strategy == "modele1":
            canal = CanalModele1(pts, pi, pd)            
        else:
            raise ValueError("Stratégie inconnue.")

        wrapper = ChannelWrapper(canal)

        result = wrapper.transmit(sequence)

        return {
            "input": sequence,
            "transmitted": result["output"],
            "errors": result["errors"],
            "channel": strategy
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/protection")
def protection(sequence: str, mode: str = "protect", factor: int = 3, strategy: str = "replication"):
    try:
        if strategy != "replication":
            raise ValueError("Stratégie inconnue.")

        wrapper = ProtectionWrapper(ReplicationProtection(factor=factor))

        if mode == "protect":
            result = wrapper.protect(sequence)
            return {
                "input": sequence,
                "output": result,
                "mode": mode,
                "protection": strategy
            }

        if mode == "restore":
            restore = wrapper.restore(sequence)
            return {
                "input": sequence,
                "output": restore["output"],
                "corrections": restore["corrections"],
                "mode": mode,
                "protection": strategy
            }

        raise ValueError("Mode inconnu, choisir 'protect' ou 'restore'.")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
