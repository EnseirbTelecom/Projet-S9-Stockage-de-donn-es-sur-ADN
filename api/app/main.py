from fastapi import FastAPI, HTTPException

from app.encoders.one2one_encoder import One2OneEncoder
from app.encoders.gray_encoder import GrayEncoder

from app.decoders.one2one_decoder import One2OneDecoder
from app.decoders.gray_decoder import GrayDecoder

from app.wrappers.encode import EncodeWrapper
from app.wrappers.decode import DecodeWrapper

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/encode")
def encode(data: str, strategy: str):
    try:
        if strategy == "one2one":
            encoder = One2OneEncoder()
        elif strategy == "gray":
            encoder = GrayEncoder()
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

@app.get("/decode")
def decode(sequence:str, strategy:str):
    try:
        if strategy == "one2one":
            decoder = One2OneDecoder()
        elif strategy == "gray":
            decoder = GrayDecoder()
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