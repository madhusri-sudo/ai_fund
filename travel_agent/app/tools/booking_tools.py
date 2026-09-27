import json

from langchain.tools import tool

from app.services import booking_service


@tool
def book_flight(
    flight_number: str,
    customer_name: str,
    departure_date: str = "",
) -> str:
    """
    Book a flight for a customer using the flight number.

    Args:
        flight_number: Flight number such as AI202.
        customer_name: Passenger / customer name.
        departure_date: Optional YYYY-MM-DD if needed to disambiguate.
    """
    try:
        booking = booking_service.book_flight(
            flight_number=flight_number,
            customer_name=customer_name,
            departure_date=departure_date or None,
        )
    except Exception as exc:
        return f"Failed to book flight: {exc}"

    return (
        "Flight booked successfully.\n"
        + json.dumps(booking, indent=2)
    )


@tool
def book_hotel(
    hotel_id: int,
    customer_name: str,
    check_in: str,
    check_out: str,
) -> str:
    """
    Book a hotel stay for a customer.

    Args:
        hotel_id: Numeric hotel id from get_hotels results.
        customer_name: Guest / customer name.
        check_in: Check-in date YYYY-MM-DD.
        check_out: Check-out date YYYY-MM-DD.
    """
    try:
        booking = booking_service.book_hotel(
            hotel_id=hotel_id,
            customer_name=customer_name,
            check_in=check_in,
            check_out=check_out,
        )
    except Exception as exc:
        return f"Failed to book hotel: {exc}"

    return (
        "Hotel booked successfully.\n"
        + json.dumps(booking, indent=2)
    )


@tool
def cancel_booking(booking_id: str) -> str:
    """
    Cancel an existing flight or hotel booking.

    Args:
        booking_id: Booking id such as BK-XXXXXXXXXX.
    """
    try:
        booking = booking_service.cancel_booking(booking_id=booking_id)
    except Exception as exc:
        return f"Failed to cancel booking: {exc}"

    return (
        "Booking cancelled successfully.\n"
        + json.dumps(booking, indent=2)
    )
