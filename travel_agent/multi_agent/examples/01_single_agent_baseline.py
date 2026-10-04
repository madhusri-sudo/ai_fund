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

from multi_agent.llm import invoke_text

SYSTEM = """
You are a single travel assistant.
Handle flights, hotels, and itinerary planning yourself in one response.
"""


def main() -> None:
    query = (
        "Book me a flight from Hyderabad to Delhi, find a hotel near the airport, "
        "and prepare my itinerary for 3 days."
    )
    print("=== Single Agent Baseline ===\n")
    print(invoke_text(SYSTEM, query))


if __name__ == "__main__":
    main()
