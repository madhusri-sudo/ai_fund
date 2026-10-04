"""
Topic: Bad vs good agent boundaries.

No LLM required. Useful presentation demo.
"""

from __future__ import annotations


BAD_FLIGHT_AGENT = """
You are a travel agent.
Search flights, recommend hotels, create itinerary,
and also decide booking policy.
"""

GOOD_FLIGHT_AGENT = """
You are a Flight Agent.
Your only responsibility is flights.
Do not choose hotels.
Do not create the final itinerary.
"""


def main() -> None:
    print("=== BAD boundary (too broad) ===\n")
    print(BAD_FLIGHT_AGENT)
    print("Problems:")
    print("- overlaps with Hotel Agent and Itinerary Agent")
    print("- hard to test in isolation")
    print("- hard to debug which part failed")

    print("\n=== GOOD boundary (specialized) ===\n")
    print(GOOD_FLIGHT_AGENT)
    print("Benefits:")
    print("- clear ownership")
    print("- easier unit testing")
    print("- cleaner orchestration")

    print("\nTeaching point: specialization starts with prompt boundaries.")


if __name__ == "__main__":
    main()
