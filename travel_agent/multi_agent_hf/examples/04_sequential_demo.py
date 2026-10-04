"""
Topic: Sequential orchestration (fixed pipeline).

Flight → Hotel → Itinerary
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from multi_agent_hf.workflows.sequential_workflow import run_sequential


def main() -> None:
    query = (
        "Plan Hyderabad to Delhi on 2026-04-15 with airport hotel and 3-day itinerary."
    )
    result = run_sequential(query)
    print("Sequential path: Flight → Hotel → Itinerary\n")
    print("FINAL ANSWER:\n")
    print(result.get("final_answer", ""))


if __name__ == "__main__":
    main()
