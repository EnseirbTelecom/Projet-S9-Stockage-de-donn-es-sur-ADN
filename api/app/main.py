from fastapi import FastAPI, HTTPException

from app.encoders.one2one_encoder import One2OneEncoder

from app.wrappers.encode import EncodeWrapper

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/encode")
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