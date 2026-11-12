from fastapi import APIRouter, HTTPException
from app.parser.encoder_src import EncoderSrcParser

router = APIRouter(
    prefix="/communication",
    tags=["Communication"]
)

@router.post("/encode")
def encode_message(data: str):
    try:
        # TODO : Exécution de la chaîne complète
        Bin = EncoderSrcParser(data)
        # 2. Ajout des mécanismes de protection
        # 3. Transmission dans le canal
        # 4. Réception
        # 5. Décodage

        return {
            "message": "Communication effectuée",
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))