from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from urllib.parse import urlparse

import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor

from app.config.settings import get_settings


def _dsn_from_url(database_url: str) -> dict[str, str | int]:
    """Parse postgresql[+psycopg2]://user:pass@host:port/db into connect kwargs."""
    normalized = database_url.replace("postgresql+psycopg2://", "postgresql://", 1)
    parsed = urlparse(normalized)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5433,
        "user": parsed.username or "postgres",
        "password": parsed.password or "postgres",
        "dbname": (parsed.path or "/travel_agent").lstrip("/") or "travel_agent",
    }


def get_connection() -> PgConnection:
    """Open a new Postgres connection."""
    settings = get_settings()
    conn = psycopg2.connect(**_dsn_from_url(settings.database_url))
    return conn


@contextmanager
def connection_scope() -> Generator[PgConnection, None, None]:
    """Transactional connection scope (commit on success, rollback on error)."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_cursor(conn: PgConnection) -> RealDictCursor:
    return conn.cursor(cursor_factory=RealDictCursor)
