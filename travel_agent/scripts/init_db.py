"""Create database tables with plain SQL on Postgres."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from app.database.connection import get_connection
from app.database.schema import SCHEMA_SQL
from scripts.ensure_db import ensure_database


def main() -> None:
    ensure_database()
    print("Creating tables...")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()
    print("Done. Tables are ready.")


if __name__ == "__main__":
    main()
