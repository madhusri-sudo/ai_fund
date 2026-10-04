"""
CLI entry for multi-agent travel orchestration demos.

Usage (from travel_agent/):
  python -m multi_agent.main sequential
  python -m multi_agent.main supervisor
  python -m multi_agent.main both
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from multi_agent.workflows.sequential_workflow import run_sequential
from multi_agent.workflows.supervisor_workflow import run_supervisor


DEFAULT_QUERY = (
    "Plan a trip from Hyderabad to Delhi on 2026-04-15: "
    "find a flight, a hotel near the airport, and prepare a 3-day itinerary."
)


def _print_sequential(request: str) -> None:
    print("\n" + "=" * 60)
    print("SEQUENTIAL WORKFLOW: Flight → Hotel → Itinerary")
    print("=" * 60)
    result = run_sequential(request)
    print("\n[1] FLIGHT FINDINGS\n")
    print(result.get("flights", ""))
    print("\n[2] HOTEL FINDINGS\n")
    print(result.get("hotels", ""))
    print("\n[3] FINAL ITINERARY\n")
    print(result.get("final_answer", ""))


def _print_supervisor(request: str) -> None:
    print("\n" + "=" * 60)
    print("SUPERVISOR WORKFLOW: dynamic routing")
    print("=" * 60)
    result = run_supervisor(request)
    print("\nRouting steps:")
    for step in result.get("steps") or []:
        print(f"  - {step}")
    print("\n[FLIGHTS]\n")
    print(result.get("flights") or "(not used)")
    print("\n[HOTELS]\n")
    print(result.get("hotels") or "(not used)")
    print("\n[FINAL]\n")
    print(
        result.get("final_answer")
        or result.get("itinerary")
        or result.get("flights")
        or result.get("hotels")
        or "(empty)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Travel multi-agent demos")
    parser.add_argument(
        "mode",
        choices=["sequential", "supervisor", "both"],
        help="Which orchestration pattern to run",
    )
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help="Travel request text",
    )
    args = parser.parse_args()

    print(f"Query: {args.query}")

    if args.mode in {"sequential", "both"}:
        _print_sequential(args.query)
    if args.mode in {"supervisor", "both"}:
        _print_supervisor(args.query)


if __name__ == "__main__":
    main()
