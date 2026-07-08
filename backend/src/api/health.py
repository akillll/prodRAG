from fastapi import APIRouter
from sqlalchemy import text

from core.config import get_settings
from db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
    }


@router.get("/ready")
def ready() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"status": "ready"}
