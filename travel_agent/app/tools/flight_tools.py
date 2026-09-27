import json

from langchain.tools import tool

from app.services import flight_service


@tool
def get_flights(
    origin: str,
    destination: str,
    departure_date: str,
) -> str:
    """
    Search available flights between two cities on a given date.

    Args:
        origin: Departure city (e.g. Hyderabad).
        destination: Arrival city (e.g. Delhi).
        departure_date: Travel date in YYYY-MM-DD format.
    """
    try:
        flights = flight_service.get_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
        )
    except Exception as exc:
        return f"Failed to search flights: {exc}"

    if not flights:
        return (
            f"No flights found from {origin} to {destination} "
            f"on {departure_date}."
        )

    return json.dumps(flights, indent=2)
