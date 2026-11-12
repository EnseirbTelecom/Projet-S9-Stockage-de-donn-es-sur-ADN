from fastapi import FastAPI

from app.routers.tests import router as tests_router
from app.routers.communication import router as com_router

app = FastAPI()

app.include_router(tests_router)
app.include_router(com_router)

@app.get("/health")
async def health():
    return {"status": "ok"}