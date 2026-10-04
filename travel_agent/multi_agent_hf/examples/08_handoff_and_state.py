"""
Topic: Weak handoff vs structured handoff / shared state.

No LLM required.
"""

from __future__ import annotations

import json


def main() -> None:
    print("=== Weak handoff ===\n")
    print('Flight Agent → Hotel Agent: "Please handle this."')
    print("Hotel Agent has almost no context.\n")

    print("=== Structured handoff ===\n")
    handoff = {
        "task": "Find hotel near arrival airport",
        "origin": "Hyderabad",
        "destination": "Delhi",
        "arrival_time": "21:30",
        "nights": 3,
        "preference": "near airport, late check-in",
        "previous_steps": ["Flight shortlist completed"],
        "expected_action": "Recommend 2-3 hotels and one top choice",
    }
    print(json.dumps(handoff, indent=2))

    print("\n=== Shared state view ===\n")
    state = {
        "request": "HYD to DEL trip with airport hotel",
        "flights": "Evening HYD-DEL arrives 21:30",
        "hotels": "",
        "itinerary": "",
    }
    print(json.dumps(state, indent=2))
    print(
        "\nNote: structured context prevents the next agent "
        "from guessing."
    )


if __name__ == "__main__":
    main()
