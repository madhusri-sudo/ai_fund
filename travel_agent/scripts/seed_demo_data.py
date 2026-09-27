"""Insert demo flights and hotels."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from app.data.seed_data import DEMO_FLIGHTS, DEMO_HOTELS
from app.database.connection import connection_scope
from app.database.repository import TravelRepository
from app.services.flight_service import add_flight
from app.services.hotel_service import add_hotel


def main() -> None:
    print("Seeding demo flights...")
    for flight in DEMO_FLIGHTS:
        with connection_scope() as conn:
            repo = TravelRepository(conn)
            existing = repo.get_flight_by_number(
                flight["flight_number"],
                flight["departure_date"],
            )

        if existing:
            print(
                f"  skip {flight['flight_number']} "
                f"on {flight['departure_date']} (already present)"
            )
            continue

        created = add_flight(**flight)
        print(f"  added flight {created['flight_number']}")

    print("\nSeeding demo hotels...")
    with connection_scope() as conn:
        repo = TravelRepository(conn)
        existing_hotels = {
            (hotel["name"].lower(), hotel["city"].lower())
            for hotel in repo.get_hotels()
        }

    for hotel in DEMO_HOTELS:
        key = (hotel["name"].lower(), hotel["city"].lower())
        if key in existing_hotels:
            print(f"  skip hotel {hotel['name']} in {hotel['city']}")
            continue

        created = add_hotel(**hotel)
        print(f"  added hotel id={created['id']} {created['name']}")

    print("\nDemo data ready.")


if __name__ == "__main__":
    main()
