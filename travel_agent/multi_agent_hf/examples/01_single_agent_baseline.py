"""
Topic: Single Agent baseline (before multi-agent).

Shows one agent trying to handle flight + hotel + itinerary alone.
Compare this later with specialized agents.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from multi_agent_hf.llm import invoke_text

SYSTEM = """
You are a single travel assistant baseline (NO database access).
This demo intentionally does not query Postgres.
Compare with examples/02_unit_test_each_agent.py which uses real inventory.
"""


def main() -> None:
    query = (
        "Book me a flight from Hyderabad to Delhi, find a hotel near the airport, "
        "and prepare my itinerary for 3 days."
    )
    print("=== Single Agent Baseline (LLM only, no Postgres) ===\n")
    print(
        "NOTE: This baseline does not use the database.\n"
        "For Postgres-backed answers run:\n"
        "  python multi_agent_hf/examples/02_unit_test_each_agent.py\n"
    )
    print(invoke_text(SYSTEM, query))


if __name__ == "__main__":
    main()
