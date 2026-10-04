"""
Topic: Shared State — the shared workspace between agents.

No LLM calls. Pure teaching demo of how state evolves.
"""

from __future__ import annotations

from typing import TypedDict


class TravelState(TypedDict):
    request: str
    flights: str
    hotels: str
    itinerary: str
    final_answer: str


def show(label: str, state: TravelState) -> None:
    print(f"\n--- {label} ---")
    for key, value in state.items():
        preview = value if value else "(empty)"
        if len(preview) > 80:
            preview = preview[:77] + "..."
        print(f"  {key}: {preview}")


def main() -> None:
    state: TravelState = {
        "request": "Hyderabad to Delhi trip, hotel + itinerary",
        "flights": "",
        "hotels": "",
        "itinerary": "",
        "final_answer": "",
    }
    show("Initial state", state)

    # Simulate Flight Agent writing into shared state
    state["flights"] = "Morning HYD-DEL flight ~₹4500 recommended."
    show("After Flight Agent", state)

    # Simulate Hotel Agent
    state["hotels"] = "Airport hotel 4-star ~₹3500/night recommended."
    show("After Hotel Agent", state)

    # Simulate Itinerary Agent
    state["itinerary"] = "Day1 arrive + check-in; Day2 meetings; Day3 return."
    state["final_answer"] = state["itinerary"]
    show("After Itinerary Agent", state)

    print(
        "\nTeaching point: agents collaborate through shared state, "
        "not by re-asking the user every time."
    )


if __name__ == "__main__":
    main()
