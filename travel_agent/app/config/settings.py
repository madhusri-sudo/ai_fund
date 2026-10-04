from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Change the Gemini model name HERE only.
# Used by single-agent (app/) and multi-agent (multi_agent/).
# Examples: "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"
# ---------------------------------------------------------------------------
GEMINI_MODEL = "gemini-3.7-flash"


class Settings(BaseSettings):
    """Runtime settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_api_key: str = ""
    gemini_api_key: str = ""
    hf_token: str = ""
    huggingfacehub_api_token: str = ""

    @property
    def gemini_model(self) -> str:
        """Always reads the GEMINI_MODEL constant above (not from .env)."""
        return GEMINI_MODEL

    @property
    def resolved_google_api_key(self) -> str:
        return self.google_api_key or self.gemini_api_key

    @property
    def resolved_hf_token(self) -> str:
        return self.hf_token or self.huggingfacehub_api_token

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
