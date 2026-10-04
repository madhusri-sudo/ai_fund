"""
Inventory access for multi_agent_hf.

1) Prefer live Postgres via app services
2) If DB is down / empty, fall back to app.data.seed_data
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any


def _as_date_str(value: Any) -> str:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value)


def _normalize_flight(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if "departure_date" in out:
        out["departure_date"] = _as_date_str(out["departure_date"])
    return out


def get_flights_inventory(
    origin: str,
    destination: str,
    departure_date: str,
) -> tuple[list[dict[str, Any]], str]:
    """
    Returns (rows, source_label).
    source_label is 'postgres' or 'seed_data'.
    """
    db_error = "incomplete lookup fields"
    if origin and destination and departure_date:
        try:
            from app.services import flight_service

            rows = flight_service.get_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
            )
            if rows:
                return [_normalize_flight(r) for r in rows], "postgres"
            db_error = "no matching rows"
        except Exception as exc:
            db_error = str(exc)

    # Fallback to in-repo seed inventory
    from app.data.seed_data import DEMO_FLIGHTS

    rows = []
    for flight in DEMO_FLIGHTS:
        if (
            str(flight["origin"]).lower() == origin.lower()
            and str(flight["destination"]).lower() == destination.lower()
            and _as_date_str(flight["departure_date"]) == departure_date
        ):
            rows.append(_normalize_flight(flight))

    return rows, f"seed_data (postgres unavailable or empty: {db_error})"


def get_hotels_inventory(city: str) -> tuple[list[dict[str, Any]], str]:
    db_error = "missing city"
    if city:
        try:
            from app.services import hotel_service

            rows = hotel_service.get_hotels(city=city)
            if rows:
                return list(rows), "postgres"
            db_error = "no matching rows"
        except Exception as exc:
            db_error = str(exc)

    from app.data.seed_data import DEMO_HOTELS

    rows = [
        dict(hotel)
        for hotel in DEMO_HOTELS
        if str(hotel["city"]).lower() == city.lower()
    ]
    return rows, f"seed_data (postgres unavailable or empty: {db_error})"
