from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from app.database.connection import connection_scope
from app.database.repository import TravelRepository


def book_flight(
    flight_number: str,
    customer_name: str,
    departure_date: str | date | None = None,
) -> dict[str, Any]:
    parsed_date = _parse_date(departure_date) if departure_date else None

    with connection_scope() as conn:
        repo = TravelRepository(conn)
        flight = repo.get_flight_by_number(flight_number, parsed_date)

        if flight is None:
            raise ValueError(f"Flight {flight_number} was not found.")

        if flight["seats_available"] < 1:
            raise ValueError(f"Flight {flight_number} has no seats available.")

        repo.decrement_flight_seats(flight, seats=1)

        booking_id = _new_booking_id()
        departure_date_value = flight["departure_date"]
        departure_date_text = (
            departure_date_value.isoformat()
            if hasattr(departure_date_value, "isoformat")
            else str(departure_date_value)
        )
        details = (
            f"{flight['airline']} {flight['flight_number']}: "
            f"{flight['origin']} -> {flight['destination']} on "
            f"{departure_date_text} "
            f"({flight['departure_time']}-{flight['arrival_time']})"
        )
        booking = repo.create_booking(
            booking_id=booking_id,
            booking_type="flight",
            customer_name=customer_name,
            reference=flight["flight_number"],
            details=details,
            total_price=float(flight["price"]),
        )
        return repo.booking_to_dict(booking)


def book_hotel(
    hotel_id: int,
    customer_name: str,
    check_in: str | date,
    check_out: str | date,
) -> dict[str, Any]:
    check_in_date = _parse_date(check_in)
    check_out_date = _parse_date(check_out)

    if check_out_date <= check_in_date:
        raise ValueError("check_out must be after check_in.")

    nights = (check_out_date - check_in_date).days

    with connection_scope() as conn:
        repo = TravelRepository(conn)
        hotel = repo.get_hotel_by_id(hotel_id)

        if hotel is None:
            raise ValueError(f"Hotel id {hotel_id} was not found.")

        if hotel["rooms_available"] < 1:
            raise ValueError(f"Hotel '{hotel['name']}' has no rooms available.")

        repo.decrement_hotel_rooms(hotel, rooms=1)

        total_price = float(hotel["price_per_night"]) * nights
        booking_id = _new_booking_id()
        details = (
            f"{hotel['name']} ({hotel['stars']}★) in {hotel['city']} "
            f"for {nights} night(s)"
        )
        booking = repo.create_booking(
            booking_id=booking_id,
            booking_type="hotel",
            customer_name=customer_name,
            reference=str(hotel["id"]),
            details=details,
            total_price=total_price,
            check_in=check_in_date,
            check_out=check_out_date,
        )
        return repo.booking_to_dict(booking)


def cancel_booking(booking_id: str) -> dict[str, Any]:
    with connection_scope() as conn:
        repo = TravelRepository(conn)
        booking = repo.get_booking(booking_id)

        if booking is None:
            raise ValueError(f"Booking {booking_id} was not found.")

        if booking["status"] == "cancelled":
            raise ValueError(f"Booking {booking_id} is already cancelled.")

        if booking["booking_type"] == "flight":
            flight = repo.get_flight_by_number(booking["reference"])
            if flight is not None:
                repo.increment_flight_seats(flight, seats=1)
        elif booking["booking_type"] == "hotel":
            try:
                hotel_id = int(booking["reference"])
            except ValueError:
                hotel_id = None
            if hotel_id is not None:
                hotel = repo.get_hotel_by_id(hotel_id)
                if hotel is not None:
                    repo.increment_hotel_rooms(hotel, rooms=1)

        cancelled = repo.cancel_booking(booking)
        return repo.booking_to_dict(cancelled)


def _new_booking_id() -> str:
    return f"BK-{uuid.uuid4().hex[:10].upper()}"


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value.strip())
