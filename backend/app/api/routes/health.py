from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.session import AsyncSessionLocal

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "service": "blackbox-api",
            "database": "connected",
            "environment": settings.app_env,
        }

    except Exception as exc:
        response = {
            "status": "degraded",
            "service": "blackbox-api",
            "database": "disconnected",
            "environment": settings.app_env,
        }

        if settings.app_env == "development":
            response["error"] = str(exc)

        return response
