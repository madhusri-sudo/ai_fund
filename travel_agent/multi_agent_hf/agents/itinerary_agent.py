"""Itinerary agent — builds plan from prior Postgres-backed findings."""

from __future__ import annotations

import re

from multi_agent_hf.llm import invoke_text
from multi_agent_hf.trip_parse import extract_trip_fields


ITINERARY_SYSTEM_PROMPT = """
You are an Itinerary Agent.

Use ONLY the flight and hotel findings provided below.
Do NOT invent flight numbers, hotel names, or prices.
If findings say they are FROM POSTGRES, copy those facts exactly.
"""


def _deterministic_itinerary(
    request: str,
    flight_findings: str,
    hotel_findings: str,
) -> str:
    fields = extract_trip_fields(request, flight_findings)
    flight_rec = ""
    hotel_rec = ""

    for line in (flight_findings or "").splitlines():
        if line.startswith("Recommendation (from inventory):"):
            flight_rec = line.replace("Recommendation (from inventory):", "").strip()
            break
    for line in (hotel_findings or "").splitlines():
        if line.startswith("Recommendation (from inventory):"):
            hotel_rec = line.replace("Recommendation (from inventory):", "").strip()
            break

    days = 3
    day_match = re.search(r"(\d+)\s*-?\s*day", request, flags=re.I)
    if day_match:
        days = max(1, min(7, int(day_match.group(1))))

    lines = [
        "Final itinerary (grounded in Postgres findings)",
        "----------------------------------------------",
        f"Request: {request}",
        f"Route: {fields.get('origin') or '?'} -> {fields.get('destination') or fields.get('city') or '?'}",
        f"Date: {fields.get('departure_date') or '(see flight findings)'}",
        "",
        f"Recommended flight: {flight_rec or '(see flight findings above)'}",
        f"Recommended hotel: {hotel_rec or '(see hotel findings above)'}",
        "",
        "Day-by-day outline:",
    ]
    for day in range(1, days + 1):
        if day == 1:
            lines.append(
                f"Day {day}: Travel / arrival, hotel check-in, light rest or nearby meal."
            )
        elif day == days:
            lines.append(
                f"Day {day}: Wrap-up, checkout, transfer, return travel as needed."
            )
        else:
            lines.append(
                f"Day {day}: Main activities / meetings in "
                f"{fields.get('destination') or fields.get('city') or 'destination city'}."
            )

    lines.extend(
        [
            "",
            "Notes:",
            "- Flight and hotel facts above come from database-backed agent outputs.",
            "- Small local HF models are not used to invent inventory.",
            "",
            "----- Source: Flight findings -----",
            flight_findings or "(none)",
            "",
            "----- Source: Hotel findings -----",
            hotel_findings or "(none)",
        ]
    )
    return "\n".join(lines)


def run_itinerary_agent(
    request: str,
    flight_findings: str = "",
    hotel_findings: str = "",
) -> str:
    """
    Build final itinerary from prior agent outputs.

    Uses a deterministic grounded plan so local HF demos stay factual.
    Optionally tries a short LLM polish; falls back if model is weak/unavailable.
    """
    grounded = _deterministic_itinerary(request, flight_findings, hotel_findings)

    # Keep LLM optional/secondary — never replace Postgres facts.
    try:
        polished = invoke_text(
            ITINERARY_SYSTEM_PROMPT,
            (
                "Rewrite the following grounded itinerary more cleanly in under 20 lines. "
                "Do not add new flights/hotels/prices.\n\n"
                f"{grounded}"
            ),
            temperature=0.1,
        )
        if polished and "AI202" in grounded and "AI202" in polished:
            return (
                polished.strip()
                + "\n\n----- Grounded source (Postgres-backed) -----\n"
                + grounded
            )
    except Exception:
        pass

    return grounded


if __name__ == "__main__":
    sample_request = "Plan a 3-day Hyderabad to Delhi business trip on 2026-10-10."
    sample_flights = (
        "Recommendation (from inventory): 6E451 (IndiGo) at ₹4500.0 departing 09:15."
    )
    sample_hotels = (
        "Recommendation (from inventory): Lotus Inn — ₹5600.0/night at Aerocity, New Delhi."
    )
    print("=== Itinerary Agent ===\n")
    print(
        run_itinerary_agent(
            sample_request,
            flight_findings=sample_flights,
            hotel_findings=sample_hotels,
        )
    )
