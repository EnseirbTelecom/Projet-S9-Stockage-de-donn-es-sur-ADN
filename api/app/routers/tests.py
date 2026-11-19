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

@router.get("/encode")
def encode(data: str, strategy: str = "one2one"):
    try:
        wrapper = EncodeWrapper(get_strategy("encoder", strategy)())

        result = wrapper.encode(data)

        return {
            "input": data,
            "encoded": result,
            "encoder": strategy
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/decode")
def decode(sequence: str, strategy: str = "one2one"):
    try:
        wrapper = DecodeWrapper(get_strategy("decoder", strategy)())

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
