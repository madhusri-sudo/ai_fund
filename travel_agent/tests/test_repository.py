"""Basic repository tests against local Postgres (isolated rows only)."""

from __future__ import annotations

from datetime import date

from app.database.connection import get_connection
from app.database.repository import TravelRepository


def test_add_and_get_flights() -> None:
    conn = get_connection()
    try:
        repo = TravelRepository(conn)
        flight = repo.add_flight(
            flight_number="ZZ999",
            airline="Test Air",
            origin="Hyderabad",
            destination="Delhi",
            departure_date=date(2099, 12, 31),
            departure_time="06:30",
            arrival_time="08:45",
            price=5200.0,
            seats_available=12,
        )
        conn.commit()

        flights = repo.get_flights(
            origin="Hyderabad",
            destination="Delhi",
            departure_date=date(2099, 12, 31),
        )
        assert len(flights) == 1
        assert flights[0]["flight_number"] == "ZZ999"
        assert float(flights[0]["price"]) == 5200.0
    finally:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM flights WHERE flight_number = %s AND departure_date = %s",
                ("ZZ999", date(2099, 12, 31)),
            )
        conn.commit()
        conn.close()


def test_add_and_get_hotels() -> None:
    conn = get_connection()
    try:
        repo = TravelRepository(conn)
        hotel = repo.add_hotel(
            name="CityStay Delhi TestZZ",
            city="Delhi",
            address="Karol Bagh",
            stars=3,
            price_per_night=3200.0,
            rooms_available=18,
            amenities="WiFi",
        )
        conn.commit()

        hotels = [
            row
            for row in repo.get_hotels(city="Delhi")
            if row["name"] == "CityStay Delhi TestZZ"
        ]
        assert len(hotels) == 1
        assert hotel["id"] == hotels[0]["id"]
    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM hotels WHERE name = %s", ("CityStay Delhi TestZZ",))
        conn.commit()
        conn.close()


def test_booking_and_cancel_restores_inventory() -> None:
    conn = get_connection()
    try:
        repo = TravelRepository(conn)
        flight = repo.add_flight(
            flight_number="ZZ451",
            airline="IndiGo",
            origin="Hyderabad",
            destination="Delhi",
            departure_date=date(2099, 1, 1),
            departure_time="09:15",
            arrival_time="11:20",
            price=4500.0,
            seats_available=2,
        )
        conn.commit()

        updated = repo.decrement_flight_seats(flight, seats=1)
        booking = repo.create_booking(
            booking_id="BK-TESTZZ001",
            booking_type="flight",
            customer_name="Madhu",
            reference=flight["flight_number"],
            details="test booking",
            total_price=float(flight["price"]),
        )
        conn.commit()

        assert updated["seats_available"] == 1
        assert booking["status"] == "confirmed"

        cancelled = repo.cancel_booking(booking)
        restored = repo.increment_flight_seats(updated, seats=1)
        conn.commit()

        assert cancelled["status"] == "cancelled"
        assert restored["seats_available"] == 2
    finally:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM bookings WHERE booking_id = %s", ("BK-TESTZZ001",))
            cur.execute(
                "DELETE FROM flights WHERE flight_number = %s AND departure_date = %s",
                ("ZZ451", date(2099, 1, 1)),
            )
        conn.commit()
        conn.close()
