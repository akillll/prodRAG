from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "prodRAG"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://prodrag:prodrag@localhost:5432/prodrag"

    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_generation_model: str = "gpt-4.1-mini"

    document_storage_path: Path = Path("./data/documents")

    otel_enabled: bool = False
    otel_exporter_otlp_endpoint: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
