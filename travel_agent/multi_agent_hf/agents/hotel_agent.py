"""Hotel specialist agent — uses Postgres (or seed fallback), never invents inventory."""

from __future__ import annotations

import json
from typing import Any

from multi_agent_hf.inventory import get_hotels_inventory
from multi_agent_hf.trip_parse import extract_trip_fields


def _prefer_airport(request: str, hotels: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not hotels:
        return None
    want_airport = "airport" in request.lower()
    if want_airport:
        for hotel in hotels:
            address = str(hotel.get("address", "")).lower()
            amenities = str(hotel.get("amenities", "")).lower()
            name = str(hotel.get("name", "")).lower()
            if "aero" in address or "airport" in amenities or "airport" in name:
                return hotel
    available = [h for h in hotels if int(h.get("rooms_available") or 0) > 0]
    pool = available or hotels
    return min(pool, key=lambda h: float(h.get("price_per_night") or 1e18))


def _format_hotels(
    hotels: list[dict[str, Any]],
    city: str,
    request: str,
    source: str,
) -> str:
    lines = [
        "Hotel findings (FROM INVENTORY — not model invention)",
        "----------------------------------------------------",
        f"Source: {source}",
        f"Lookup city: {city or '(unknown)'}",
        "",
    ]
    if not hotels:
        lines.append(
            "No matching hotels found.\n"
            "Seed cities include: Delhi, Mumbai, Hyderabad.\n"
            "If using Postgres: python scripts/seed_demo_data.py"
        )
        return "\n".join(lines)

    lines.append(f"Found {len(hotels)} hotel(s):")
    for idx, hotel in enumerate(hotels, start=1):
        lines.extend(
            [
                f"{idx}. {hotel.get('name')} ({hotel.get('stars')} stars)",
                f"   City: {hotel.get('city')}",
                f"   Address: {hotel.get('address')}",
                f"   Price/night: INR {hotel.get('price_per_night')}",
                f"   Rooms available: {hotel.get('rooms_available')}",
                f"   Amenities: {hotel.get('amenities')}",
                "",
            ]
        )

    pick = _prefer_airport(request, hotels)
    if pick:
        lines.append(
            "Recommendation (from inventory): "
            f"{pick.get('name')} - INR {pick.get('price_per_night')}/night "
            f"at {pick.get('address')}."
        )
    lines.append("")
    lines.append("Raw inventory JSON:")
    lines.append(json.dumps(hotels, indent=2, default=str))
    return "\n".join(lines)


def run_hotel_agent(request: str, flight_findings: str = "") -> str:
    """Run hotel agent using real inventory (Postgres first, seed fallback)."""
    fields = extract_trip_fields(request, flight_findings=flight_findings)
    city = fields["city"] or fields["destination"]
    hotels, source = get_hotels_inventory(city)
    return _format_hotels(hotels, city, request, source)


def run_hotel_agent_with_tools(request: str) -> str:
    raise RuntimeError(
        "Use multi_agent (Gemini) for LangChain tool-calling demos. "
        "multi_agent_hf hotel agent reads inventory directly."
    )


if __name__ == "__main__":
    sample = "I need a hotel near the airport in Delhi for a 3-day business trip."
    print("=== Hotel Agent (inventory-backed) ===\n")
    print(run_hotel_agent(sample))
