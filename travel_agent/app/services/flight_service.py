from __future__ import annotations

from datetime import date
from typing import Any

from app.database.connection import connection_scope
from app.database.repository import TravelRepository


def add_flight(
    *,
    flight_number: str,
    airline: str,
    origin: str,
    destination: str,
    departure_date: str | date,
    departure_time: str,
    arrival_time: str,
    price: float,
    seats_available: int,
) -> dict[str, Any]:
    """Reusable flight ingestion helper."""
    parsed_date = _parse_date(departure_date)

    with connection_scope() as conn:
        repo = TravelRepository(conn)
        flight = repo.add_flight(
            flight_number=flight_number,
            airline=airline,
            origin=origin,
            destination=destination,
            departure_date=parsed_date,
            departure_time=departure_time,
            arrival_time=arrival_time,
            price=price,
            seats_available=seats_available,
        )
        return repo.flight_to_dict(flight)


def get_flights(
    origin: str,
    destination: str,
    departure_date: str | date | None = None,
) -> list[dict[str, Any]]:
    parsed_date = _parse_date(departure_date) if departure_date else None

    with connection_scope() as conn:
        repo = TravelRepository(conn)
        flights = repo.get_flights(
            origin=origin,
            destination=destination,
            departure_date=parsed_date,
        )
        return [repo.flight_to_dict(flight) for flight in flights]


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value.strip())
