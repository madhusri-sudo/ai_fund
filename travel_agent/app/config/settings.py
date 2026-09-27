from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_api_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"

    @property
    def resolved_google_api_key(self) -> str:
        return self.google_api_key or self.gemini_api_key

    langchain_tracing_v2: bool = True
    langchain_api_key: str = ""
    langchain_project: str = "travel-agent"

    # Same local Postgres used by this repo (pgvector-db on port 5433).
    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5433/travel_agent"
    )

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "travel_agent"
    postgres_port: int = 5433


@lru_cache
def get_settings() -> Settings:
    return Settings()
