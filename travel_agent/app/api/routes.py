from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.services import booking_service, flight_service, hotel_service

app = FastAPI(title="Travel Agent API", version="1.0.0")


class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str = Field(..., description="YYYY-MM-DD")


class HotelSearchRequest(BaseModel):
    city: str


class BookFlightRequest(BaseModel):
    flight_number: str
    customer_name: str
    departure_date: str | None = None


class BookHotelRequest(BaseModel):
    hotel_id: int
    customer_name: str
    check_in: str
    check_out: str


class CancelBookingRequest(BaseModel):
    booking_id: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/flights/search")
def search_flights(payload: FlightSearchRequest) -> list[dict[str, Any]]:
    try:
        return flight_service.get_flights(
            origin=payload.origin,
            destination=payload.destination,
            departure_date=payload.departure_date,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/hotels/search")
def search_hotels(payload: HotelSearchRequest) -> list[dict[str, Any]]:
    try:
        return hotel_service.get_hotels(city=payload.city)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/bookings/flight")
def create_flight_booking(payload: BookFlightRequest) -> dict[str, Any]:
    try:
        return booking_service.book_flight(
            flight_number=payload.flight_number,
            customer_name=payload.customer_name,
            departure_date=payload.departure_date,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/bookings/hotel")
def create_hotel_booking(payload: BookHotelRequest) -> dict[str, Any]:
    try:
        return booking_service.book_hotel(
            hotel_id=payload.hotel_id,
            customer_name=payload.customer_name,
            check_in=payload.check_in,
            check_out=payload.check_out,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/bookings/cancel")
def cancel_existing_booking(payload: CancelBookingRequest) -> dict[str, Any]:
    try:
        return booking_service.cancel_booking(booking_id=payload.booking_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
