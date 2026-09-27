from __future__ import annotations

from datetime import date
from typing import Any

from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor


class TravelRepository:
    """Data-access layer using plain SQL via psycopg2."""

    def __init__(self, conn: PgConnection) -> None:
        self.conn = conn

    def _cursor(self) -> RealDictCursor:
        return self.conn.cursor(cursor_factory=RealDictCursor)

    # ------------------------------------------------------------------
    # Flights
    # ------------------------------------------------------------------

    def add_flight(
        self,
        *,
        flight_number: str,
        airline: str,
        origin: str,
        destination: str,
        departure_date: date,
        departure_time: str,
        arrival_time: str,
        price: float,
        seats_available: int,
    ) -> dict[str, Any]:
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO flights (
                    flight_number, airline, origin, destination,
                    departure_date, departure_time, arrival_time,
                    price, seats_available
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    flight_number.upper().strip(),
                    airline.strip(),
                    origin.strip().title(),
                    destination.strip().title(),
                    departure_date,
                    departure_time,
                    arrival_time,
                    price,
                    seats_available,
                ),
            )
            return dict(cur.fetchone())

    def get_flights(
        self,
        *,
        origin: str | None = None,
        destination: str | None = None,
        departure_date: date | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []

        if origin:
            clauses.append("origin ILIKE %s")
            params.append(origin.strip())
        if destination:
            clauses.append("destination ILIKE %s")
            params.append(destination.strip())
        if departure_date:
            clauses.append("departure_date = %s")
            params.append(departure_date)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""
            SELECT * FROM flights
            {where}
            ORDER BY departure_date, departure_time
        """

        with self._cursor() as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def get_flight_by_number(
        self,
        flight_number: str,
        departure_date: date | None = None,
    ) -> dict[str, Any] | None:
        clauses = ["flight_number = %s"]
        params: list[Any] = [flight_number.upper().strip()]

        if departure_date:
            clauses.append("departure_date = %s")
            params.append(departure_date)

        sql = f"SELECT * FROM flights WHERE {' AND '.join(clauses)} LIMIT 1"

        with self._cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None

    def decrement_flight_seats(self, flight: dict[str, Any], seats: int = 1) -> dict[str, Any]:
        if flight["seats_available"] < seats:
            raise ValueError("Not enough seats available.")

        with self._cursor() as cur:
            cur.execute(
                """
                UPDATE flights
                SET seats_available = seats_available - %s
                WHERE id = %s AND seats_available >= %s
                RETURNING *
                """,
                (seats, flight["id"], seats),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError("Not enough seats available.")
            return dict(row)

    def increment_flight_seats(self, flight: dict[str, Any], seats: int = 1) -> dict[str, Any]:
        with self._cursor() as cur:
            cur.execute(
                """
                UPDATE flights
                SET seats_available = seats_available + %s
                WHERE id = %s
                RETURNING *
                """,
                (seats, flight["id"]),
            )
            return dict(cur.fetchone())

    # ------------------------------------------------------------------
    # Hotels
    # ------------------------------------------------------------------

    def add_hotel(
        self,
        *,
        name: str,
        city: str,
        address: str = "",
        stars: int = 3,
        price_per_night: float,
        rooms_available: int,
        amenities: str = "",
    ) -> dict[str, Any]:
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO hotels (
                    name, city, address, stars,
                    price_per_night, rooms_available, amenities
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    name.strip(),
                    city.strip().title(),
                    address.strip(),
                    stars,
                    price_per_night,
                    rooms_available,
                    amenities.strip(),
                ),
            )
            return dict(cur.fetchone())

    def get_hotels(self, *, city: str | None = None) -> list[dict[str, Any]]:
        if city:
            sql = """
                SELECT * FROM hotels
                WHERE city ILIKE %s
                ORDER BY stars DESC, price_per_night
            """
            params: tuple[Any, ...] = (city.strip(),)
        else:
            sql = """
                SELECT * FROM hotels
                ORDER BY stars DESC, price_per_night
            """
            params = ()

        with self._cursor() as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def get_hotel_by_id(self, hotel_id: int) -> dict[str, Any] | None:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM hotels WHERE id = %s", (hotel_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def decrement_hotel_rooms(self, hotel: dict[str, Any], rooms: int = 1) -> dict[str, Any]:
        if hotel["rooms_available"] < rooms:
            raise ValueError("Not enough rooms available.")

        with self._cursor() as cur:
            cur.execute(
                """
                UPDATE hotels
                SET rooms_available = rooms_available - %s
                WHERE id = %s AND rooms_available >= %s
                RETURNING *
                """,
                (rooms, hotel["id"], rooms),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError("Not enough rooms available.")
            return dict(row)

    def increment_hotel_rooms(self, hotel: dict[str, Any], rooms: int = 1) -> dict[str, Any]:
        with self._cursor() as cur:
            cur.execute(
                """
                UPDATE hotels
                SET rooms_available = rooms_available + %s
                WHERE id = %s
                RETURNING *
                """,
                (rooms, hotel["id"]),
            )
            return dict(cur.fetchone())

    # ------------------------------------------------------------------
    # Bookings
    # ------------------------------------------------------------------

    def create_booking(
        self,
        *,
        booking_id: str,
        booking_type: str,
        customer_name: str,
        reference: str,
        details: str,
        total_price: float,
        check_in: date | None = None,
        check_out: date | None = None,
        status: str = "confirmed",
    ) -> dict[str, Any]:
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO bookings (
                    booking_id, booking_type, customer_name, reference,
                    details, check_in, check_out, total_price, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    booking_id,
                    booking_type,
                    customer_name.strip(),
                    reference,
                    details,
                    check_in,
                    check_out,
                    total_price,
                    status,
                ),
            )
            return dict(cur.fetchone())

    def get_booking(self, booking_id: str) -> dict[str, Any] | None:
        with self._cursor() as cur:
            cur.execute(
                "SELECT * FROM bookings WHERE booking_id = %s",
                (booking_id.strip(),),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def cancel_booking(self, booking: dict[str, Any]) -> dict[str, Any]:
        if booking["status"] == "cancelled":
            raise ValueError(f"Booking {booking['booking_id']} is already cancelled.")

        with self._cursor() as cur:
            cur.execute(
                """
                UPDATE bookings
                SET status = 'cancelled'
                WHERE booking_id = %s AND status <> 'cancelled'
                RETURNING *
                """,
                (booking["booking_id"],),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Booking {booking['booking_id']} is already cancelled.")
            return dict(row)

    @staticmethod
    def flight_to_dict(flight: dict[str, Any]) -> dict[str, Any]:
        departure_date = flight["departure_date"]
        return {
            "id": flight["id"],
            "flight_number": flight["flight_number"],
            "airline": flight["airline"],
            "origin": flight["origin"],
            "destination": flight["destination"],
            "departure_date": (
                departure_date.isoformat()
                if hasattr(departure_date, "isoformat")
                else str(departure_date)
            ),
            "departure_time": flight["departure_time"],
            "arrival_time": flight["arrival_time"],
            "price": float(flight["price"]),
            "seats_available": flight["seats_available"],
        }

    @staticmethod
    def hotel_to_dict(hotel: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": hotel["id"],
            "name": hotel["name"],
            "city": hotel["city"],
            "address": hotel["address"],
            "stars": hotel["stars"],
            "price_per_night": float(hotel["price_per_night"]),
            "rooms_available": hotel["rooms_available"],
            "amenities": hotel["amenities"],
        }

    @staticmethod
    def booking_to_dict(booking: dict[str, Any]) -> dict[str, Any]:
        check_in = booking.get("check_in")
        check_out = booking.get("check_out")
        return {
            "booking_id": booking["booking_id"],
            "booking_type": booking["booking_type"],
            "customer_name": booking["customer_name"],
            "reference": booking["reference"],
            "details": booking["details"],
            "check_in": check_in.isoformat() if check_in else None,
            "check_out": check_out.isoformat() if check_out else None,
            "total_price": float(booking["total_price"]),
            "status": booking["status"],
        }
