from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.runs import router as runs_router
from app.core.config import settings

app = FastAPI(
    title="Blackbox API",
    description="Privacy debugging backend for LLM data flows.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(runs_router)


@app.get("/")
async def root():
    return {
        "service": "Blackbox API",
        "status": "running",
        "message": "Open the hidden layer of AI.",
    }