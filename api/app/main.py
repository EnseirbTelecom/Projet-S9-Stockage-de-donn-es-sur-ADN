from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers.tests import router as tests_router
from app.routers.communication import router as com_router
from app.routers.files import router as files_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Idempotent : crée les tables manquantes (SQLite local) ou ne fait
    # rien sur PostgreSQL dont le schéma est posé par database/init.sql.
    Base.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(tests_router)
app.include_router(com_router)
app.include_router(files_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
