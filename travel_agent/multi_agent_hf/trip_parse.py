"""
Deterministic trip-field parsing for local HF demos.

Small HF models are unreliable at JSON extraction, so we parse
origin / destination / date / city with Python rules, then query Postgres.
"""

from __future__ import annotations

import re
from typing import TypedDict

# Cities that appear in seed inventory / common demos
KNOWN_CITIES = [
    "Hyderabad",
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Bangalore",
    "Chennai",
    "Goa",
    "Jaipur",
    "Pune",
]

CITY_ALIASES = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "hyd": "Hyderabad",
    "del": "Delhi",
    "bom": "Mumbai",
}


class TripFields(TypedDict):
    origin: str
    destination: str
    departure_date: str
    city: str


def _normalize_city(name: str) -> str:
    key = name.strip().lower()
    if key in CITY_ALIASES:
        return CITY_ALIASES[key]
    for city in KNOWN_CITIES:
        if city.lower() == key:
            return city
    return name.strip().title()


def _find_cities(text: str) -> list[str]:
    found: list[str] = []
    lower = text.lower()
    # Longer names first to avoid partial confusion
    candidates = sorted(KNOWN_CITIES, key=len, reverse=True)
    for city in candidates:
        if city.lower() in lower:
            norm = _normalize_city(city)
            if norm not in found:
                found.append(norm)
    # Also catch HYD → DEL style tokens
    for token in re.findall(r"\b([A-Za-z]{3})\b", text):
        alias = CITY_ALIASES.get(token.lower())
        if alias and alias not in found:
            found.append(alias)
    return found


def _find_date(text: str) -> str:
    match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if match:
        return match.group(1)
    # Default to seeded demo date when user says trip/flight but omits date
    if re.search(r"\b(flight|trip|travel|itinerary|hotel)\b", text, re.I):
        return "2026-10-10"
    return ""


def _route_from_arrows(text: str) -> tuple[str, str]:
    patterns = [
        r"([A-Za-z]+)\s*(?:→|->|to)\s*([A-Za-z]+)",
        r"from\s+([A-Za-z]+)\s+to\s+([A-Za-z]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if not match:
            continue
        origin = _normalize_city(match.group(1))
        destination = _normalize_city(match.group(2))
        # Only accept if they look like known cities (or aliases resolved)
        known = {c.lower() for c in KNOWN_CITIES} | set(CITY_ALIASES)
        if origin.lower() in known or destination.lower() in known:
            return origin, destination
    return "", ""


def extract_trip_fields(request: str, flight_findings: str = "") -> TripFields:
    """Extract trip fields without calling an LLM."""
    blob = f"{request}\n{flight_findings or ''}"
    origin, destination = _route_from_arrows(request)
    cities = _find_cities(blob)

    if not origin and len(cities) >= 2:
        # Heuristic: first city origin, second destination for "A ... B" requests
        origin, destination = cities[0], cities[1]
    elif not origin and len(cities) == 1:
        destination = cities[0]

    if not destination and cities:
        # Prefer non-origin city as destination
        for city in cities:
            if city != origin:
                destination = city
                break
        if not destination:
            destination = cities[0]

    # Hotel city preference: destination, else last mentioned city
    city = destination or (cities[-1] if cities else "")

    # If flight findings mention Delhi etc., keep that for hotel stage
    if not city and flight_findings:
        f_cities = _find_cities(flight_findings)
        if f_cities:
            city = f_cities[-1]

    return {
        "origin": origin,
        "destination": destination,
        "departure_date": _find_date(request),
        "city": city,
    }
