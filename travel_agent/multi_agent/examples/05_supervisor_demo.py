"""
Topic: Supervisor orchestration (dynamic routing).

Try different queries and observe different worker paths.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from multi_agent.workflows.supervisor_workflow import run_supervisor


QUERIES = [
    "Only research flights from Hyderabad to Delhi on 2026-04-15.",
    "Find hotels near the airport in Delhi for 3 nights.",
    (
        "Plan full trip: Hyderabad to Delhi on 2026-04-15, "
        "airport hotel, and prepare itinerary."
    ),
]


def main() -> None:
    for i, query in enumerate(QUERIES, start=1):
        print("\n" + "=" * 60)
        print(f"Query {i}: {query}")
        result = run_supervisor(query)
        print("Steps:", result.get("steps"))
        final = (
            result.get("final_answer")
            or result.get("itinerary")
            or result.get("flights")
            or result.get("hotels")
        )
        print("\nResult preview:\n")
        print((final or "")[:800])


if __name__ == "__main__":
    main()
