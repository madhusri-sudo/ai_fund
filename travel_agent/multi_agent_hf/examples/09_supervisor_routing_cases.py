"""
Topic: Supervisor routing cases for presentation.

Runs several queries and prints routing steps.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from multi_agent_hf.workflows.supervisor_workflow import run_supervisor


CASES = [
    (
        "Flight only",
        "Only research flights from Hyderabad to Delhi on 2026-04-15.",
        "Expected: flight → FINISH",
    ),
    (
        "Hotel only",
        "Find hotels near the airport in Delhi for 3 nights.",
        "Expected: hotel → FINISH",
    ),
    (
        "Full trip",
        (
            "Plan full trip: Hyderabad to Delhi on 2026-04-15, "
            "airport hotel, and prepare itinerary."
        ),
        "Expected: flight → hotel → itinerary → FINISH",
    ),
    (
        "No hotel needed",
        "Find only morning flights HYD to DEL. Do not plan hotel.",
        "Expected: flight → FINISH",
    ),
    (
        "Vague request",
        "Help me plan Delhi travel from Hyderabad.",
        "Expected: likely full planning path",
    ),
]


def main() -> None:
    for title, query, expected in CASES:
        print("\n" + "=" * 60)
        print(f"{title}")
        print(f"Query: {query}")
        print(f"{expected}")
        result = run_supervisor(query)
        print("Actual steps:", result.get("steps"))
        print("\nFinal answer (LLM):\n")
        print(result.get("final_answer") or "(empty)")


if __name__ == "__main__":
    main()
