"""Flight specialist agent — uses Postgres (or seed fallback), never invents inventory."""

from __future__ import annotations

import json
from typing import Any

from multi_agent_hf.inventory import get_flights_inventory
from multi_agent_hf.trip_parse import extract_trip_fields


def _format_flights(
    flights: list[dict[str, Any]],
    fields: dict[str, str],
    source: str,
) -> str:
    lines = [
        "Flight findings (FROM INVENTORY — not model invention)",
        "-----------------------------------------------------",
        f"Source: {source}",
        f"Lookup: {fields.get('origin')} -> {fields.get('destination')} "
        f"on {fields.get('departure_date')}",
        "",
    ]
    if not flights:
        lines.append(
            "No matching flights found.\n"
            "Expected demo routes:\n"
            "  Hyderabad -> Delhi on 2026-10-10\n"
            "  Hyderabad -> Delhi on 2026-04-15\n"
            "If using Postgres: python scripts/seed_demo_data.py"
        )
        return "\n".join(lines)

    lines.append(f"Found {len(flights)} flight(s):")
    for idx, flight in enumerate(flights, start=1):
        lines.extend(
            [
                f"{idx}. {flight.get('flight_number')} - {flight.get('airline')}",
                f"   Route: {flight.get('origin')} -> {flight.get('destination')}",
                f"   Date: {flight.get('departure_date')}",
                f"   Time: {flight.get('departure_time')} -> {flight.get('arrival_time')}",
                f"   Price: INR {flight.get('price')}",
                f"   Seats available: {flight.get('seats_available')}",
                "",
            ]
        )

    available = [f for f in flights if int(f.get("seats_available") or 0) > 0]
    pick = min(available, key=lambda f: float(f.get("price") or 1e18)) if available else flights[0]
    lines.append(
        "Recommendation (from inventory): "
        f"{pick.get('flight_number')} ({pick.get('airline')}) "
        f"at INR {pick.get('price')} departing {pick.get('departure_time')}."
    )
    lines.append("")
    lines.append("Raw inventory JSON:")
    lines.append(json.dumps(flights, indent=2, default=str))
    return "\n".join(lines)


def run_flight_agent(request: str, prior_context: str = "") -> str:
    """Run flight agent using real inventory (Postgres first, seed fallback)."""
    fields = extract_trip_fields(request)
    flights, source = get_flights_inventory(
        fields["origin"],
        fields["destination"],
        fields["departure_date"],
    )
    return _format_flights(flights, fields, source)


def run_flight_agent_with_tools(request: str) -> str:
    raise RuntimeError(
        "Use multi_agent (Gemini) for LangChain tool-calling demos. "
        "multi_agent_hf flight agent reads inventory directly."
    )


if __name__ == "__main__":
    sample = (
        "Find flights from Hyderabad to Delhi on 2026-10-10 "
        "for a 3-day business trip."
    )
    print("=== Flight Agent (inventory-backed) ===\n")
    print(run_flight_agent(sample))
