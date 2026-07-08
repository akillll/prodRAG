from fastapi import FastAPI

from api import api_router
from core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(api_router)
    return app


app = create_app()
