import json

from langchain.tools import tool

from app.services import hotel_service


@tool
def get_hotels(city: str) -> str:
    """
    Search available hotels in a city.

    Args:
        city: City name (e.g. Delhi).
    """
    try:
        hotels = hotel_service.get_hotels(city=city)
    except Exception as exc:
        return f"Failed to search hotels: {exc}"

    if not hotels:
        return f"No hotels found in {city}."

    return json.dumps(hotels, indent=2)
