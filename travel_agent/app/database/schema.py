"""Postgres DDL for the travel agent tables (no ORM)."""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS flights (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(20) NOT NULL,
    airline VARCHAR(100) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    departure_date DATE NOT NULL,
    departure_time VARCHAR(10) NOT NULL,
    arrival_time VARCHAR(10) NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    seats_available INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_flight_number_date UNIQUE (flight_number, departure_date)
);

CREATE INDEX IF NOT EXISTS ix_flights_origin ON flights (origin);
CREATE INDEX IF NOT EXISTS ix_flights_destination ON flights (destination);
CREATE INDEX IF NOT EXISTS ix_flights_departure_date ON flights (departure_date);
CREATE INDEX IF NOT EXISTS ix_flights_flight_number ON flights (flight_number);

CREATE TABLE IF NOT EXISTS hotels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(300) NOT NULL DEFAULT '',
    stars INTEGER NOT NULL DEFAULT 3,
    price_per_night DOUBLE PRECISION NOT NULL,
    rooms_available INTEGER NOT NULL DEFAULT 0,
    amenities TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_hotels_city ON hotels (city);

CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    booking_id VARCHAR(40) NOT NULL UNIQUE,
    booking_type VARCHAR(20) NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    reference VARCHAR(100) NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    check_in DATE NULL,
    check_out DATE NULL,
    total_price DOUBLE PRECISION NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_bookings_booking_id ON bookings (booking_id);
"""
