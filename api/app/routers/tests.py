from fastapi import APIRouter, HTTPException

from app.catalog import get_strategy, build_strategy

from app.wrappers.encode import EncodeWrapper
from app.wrappers.decode import DecodeWrapper
from app.wrappers.channel import ChannelWrapper
from app.wrappers.protection import ProtectionWrapper

router = APIRouter(
    prefix="/tests",
    tags=["Tests"]
)

@router.post("/encode")
def encode_message(data: str, encoder: str = "gray"):
    try:
        encoder_instance = build_strategy("encoder", encoder)
        wrapper = EncodeWrapper(encoder_instance)
        encoded = wrapper.encode(data)

        return {
            "message": "Encodage effectué",
            "data": data,
            "encoded": encoded,
            "encoder": encoder_instance.slug
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/decode")
def decode_message(data: str, decoder: str = "gray"):
    try:
        decoder_instance = build_strategy("decoder", decoder)
        wrapper = DecodeWrapper(decoder_instance)
        decoded = wrapper.decode(data)

        return {
            "message": "Décodage effectué",
            "data": data,
            "decoded": decoded,
            "decoder": decoder_instance.slug
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/channel")
def channel(sequence: str, error_rate: float = 0.05, strategy: str ="", pts: float = 0.1, pi: float = 0.1, pd: float = 0.1,seed: int | None = None):
    try:
        wrapper = ChannelWrapper(
            build_strategy("channel", strategy, error_rate=error_rate, seed=seed)
        )
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
        wrapper = ProtectionWrapper(
            build_strategy("protection", strategy, factor=factor)
        )

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
