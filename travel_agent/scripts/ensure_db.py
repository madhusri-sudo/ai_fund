"""Ensure the travel_agent database exists on the running Postgres/pgvector container."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from app.config.settings import get_settings


def ensure_database() -> str:
    settings = get_settings()
    parsed = urlparse(settings.database_url)

    db_name = (parsed.path or "/travel_agent").lstrip("/") or "travel_agent"
    user = parsed.username or "postgres"
    password = parsed.password or "postgres"
    host = parsed.hostname or "localhost"
    port = parsed.port or 5433

    admin = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname="postgres",
    )
    admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = admin.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    exists = cur.fetchone() is not None

    if not exists:
        cur.execute(f'CREATE DATABASE "{db_name}"')
        print(f"Created database: {db_name}")
    else:
        print(f"Database already exists: {db_name}")

    cur.close()
    admin.close()
    return db_name


if __name__ == "__main__":
    ensure_database()
