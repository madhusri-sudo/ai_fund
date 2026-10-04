"""
Topic: Parallel orchestration concept for travel.

No LLM required. Shows independent work then merge.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor


def flight_task(request: str) -> str:
    time.sleep(0.2)
    return "Flight shortlist: HYD-DEL morning / evening options"


def hotel_task(request: str) -> str:
    time.sleep(0.2)
    return "Hotel shortlist: airport 4-star / city 3-star"


def activities_task(request: str) -> str:
    time.sleep(0.2)
    return "Activities: India Gate, Qutub Minar, local food walk"


def main() -> None:
    request = "Plan my trip to Delhi"
    print("=== Sequential timing (conceptual) ===")
    start = time.perf_counter()
    flights = flight_task(request)
    hotels = hotel_task(request)
    activities = activities_task(request)
    sequential_ms = (time.perf_counter() - start) * 1000
    print(flights)
    print(hotels)
    print(activities)
    print(f"Approx elapsed: {sequential_ms:.0f} ms\n")

    print("=== Parallel timing (conceptual) ===")
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_future = pool.submit(flight_task, request)
        h_future = pool.submit(hotel_task, request)
        a_future = pool.submit(activities_task, request)
        flights = f_future.result()
        hotels = h_future.result()
        activities = a_future.result()
    parallel_ms = (time.perf_counter() - start) * 1000
    print(flights)
    print(hotels)
    print(activities)
    print(f"Approx elapsed: {parallel_ms:.0f} ms")

    print("\nMerged into Itinerary Agent input:")
    print(
        {
            "flights": flights,
            "hotels": hotels,
            "activities": activities,
        }
    )
    print(
        "\nTeaching point: use parallel when tasks are independent; "
        "use sequential when one output is required by the next step."
    )


if __name__ == "__main__":
    main()
