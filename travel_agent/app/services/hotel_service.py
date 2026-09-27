from __future__ import annotations

from typing import Any

from app.database.connection import connection_scope
from app.database.repository import TravelRepository


def add_hotel(
    *,
    name: str,
    city: str,
    address: str = "",
    stars: int = 3,
    price_per_night: float,
    rooms_available: int,
    amenities: str = "",
) -> dict[str, Any]:
    """Reusable hotel ingestion helper."""
    with connection_scope() as conn:
        repo = TravelRepository(conn)
        hotel = repo.add_hotel(
            name=name,
            city=city,
            address=address,
            stars=stars,
            price_per_night=price_per_night,
            rooms_available=rooms_available,
            amenities=amenities,
        )
        return repo.hotel_to_dict(hotel)


def get_hotels(city: str) -> list[dict[str, Any]]:
    with connection_scope() as conn:
        repo = TravelRepository(conn)
        hotels = repo.get_hotels(city=city)
        return [repo.hotel_to_dict(hotel) for hotel in hotels]
