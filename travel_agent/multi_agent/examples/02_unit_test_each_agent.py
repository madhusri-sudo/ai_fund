"""
Topic: Build agents independently first (unit-test style).

Run each specialist alone before orchestration.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from multi_agent.agents.flight_agent import run_flight_agent
from multi_agent.agents.hotel_agent import run_hotel_agent
from multi_agent.agents.itinerary_agent import run_itinerary_agent


def main() -> None:
    request = (
        "Flight Hyderabad → Delhi on 2026-04-15, hotel near airport, 3-day trip."
    )

    print("=== 1) Flight Agent ===\n")
    flights = run_flight_agent(request)
    print(flights)

    print("\n=== 2) Hotel Agent ===\n")
    hotels = run_hotel_agent(request, flight_findings=flights)
    print(hotels)

    print("\n=== 3) Itinerary Agent ===\n")
    plan = run_itinerary_agent(request, flights, hotels)
    print(plan)


if __name__ == "__main__":
    main()
