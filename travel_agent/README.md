# Travel Agent — Complete Guide

This document explains **what we built**, **why each file exists**, **how the database is created**, and **how data flows from start to finish**.

> This project uses a **simulated travel inventory** stored in PostgreSQL. It is **not** connected to real airline or hotel APIs. Later you can replace only the repository/service SQL with real APIs; the agent tools stay the same.

---

## 1. What this project is

A local **LangChain + Gemini** travel assistant that can:

| Capability | How it works |
|------------|--------------|
| Search flights | Queries the `flights` table in Postgres |
| Search hotels | Queries the `hotels` table |
| Book flight / hotel | Inserts into `bookings` and reduces seats/rooms |
| Cancel booking | Marks booking cancelled and restores inventory |
| Chat CLI | You talk in natural language; the agent calls tools |

**Stack**

- **LLM**: Google Gemini (`gemini-3.8-flash` by default)
- **Agent framework**: LangChain (`create_agent` + tools)
- **Database**: PostgreSQL (your existing server on `localhost:5433`)
- **DB access**: plain `psycopg2` + SQL (no SQLAlchemy / ORM)
- **Optional**: LangSmith tracing, FastAPI HTTP routes

---

## 2. How we created it (start → end)

This is the order the system was designed and built:

```text
1. Config (.env + settings)
        ↓
2. Postgres connection (psycopg2)
        ↓
3. Schema SQL (CREATE TABLE flights / hotels / bookings)
        ↓
4. Repository (raw INSERT / SELECT / UPDATE)
        ↓
5. Services (add_flight, get_flights, book_flight, ...)
        ↓
6. LangChain tools (wrappers the LLM can call)
        ↓
7. Agent + system prompt (Gemini decides when to use tools)
        ↓
8. CLI (app/main.py) — user chat loop
        ↓
9. Scripts (init_db, seed_demo_data) + tests + optional API
```

**Request path when you chat**

```text
You type a message
    → app/main.py
    → LangChain agent (Gemini)
    → tool (e.g. get_flights / book_flight)
    → service (flight_service / booking_service)
    → repository (SQL)
    → PostgreSQL (travel_agent database)
    → result back to Gemini
    → natural-language answer printed in CLI
```

---

## 3. Project structure (every file)

```text
travel_agent/
│
├── .env.example              # Template for secrets & DB URL
├── .env                      # Your real keys (gitignored)
├── .gitignore
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Optional fallback Postgres (not required)
├── pytest.ini                # Makes `pytest` find the `app` package
├── README.md                 # This guide
│
├── app/
│   ├── main.py               # CLI chat entry point
│   │
│   ├── config/
│   │   └── settings.py       # Loads .env (API keys, DATABASE_URL, model)
│   │
│   ├── database/
│   │   ├── connection.py     # psycopg2 connect + transaction helper
│   │   ├── schema.py         # CREATE TABLE SQL for flights/hotels/bookings
│   │   └── repository.py     # All SQL queries (add/get/book/cancel)
│   │
│   ├── services/
│   │   ├── flight_service.py # add_flight(), get_flights()
│   │   ├── hotel_service.py  # add_hotel(), get_hotels()
│   │   └── booking_service.py# book_flight(), book_hotel(), cancel_booking()
│   │
│   ├── tools/
│   │   ├── flight_tools.py   # LangChain @tool → get_flights
│   │   ├── hotel_tools.py    # LangChain @tool → get_hotels
│   │   └── booking_tools.py  # LangChain @tool → book / cancel
│   │
│   ├── agent/
│   │   ├── prompts.py        # System instructions for the agent
│   │   └── travel_agent.py   # Builds Gemini model + tools + agent
│   │
│   ├── data/
│   │   └── seed_data.py      # Demo flight & hotel rows (Python lists)
│   │
│   └── api/
│       └── routes.py         # Optional FastAPI HTTP endpoints
│
├── scripts/
│   ├── ensure_db.py          # CREATE DATABASE travel_agent if missing
│   ├── init_db.py            # ensure_db + run SCHEMA_SQL
│   └── seed_demo_data.py     # Insert demo flights/hotels via services
│
└── tests/
    └── test_repository.py    # Basic Postgres SQL tests
```

---

## 4. What each important file does

### Root / config

| File | Purpose |
|------|---------|
| `requirements.txt` | Installs LangChain, Gemini SDK, `psycopg2-binary`, FastAPI, pytest, etc. |
| `.env.example` | Safe template. Copy to `.env` and fill keys. |
| `.env` | Real `GEMINI_API_KEY`, `DATABASE_URL`, `GEMINI_MODEL`. **Do not commit.** |
| `docker-compose.yml` | Optional standalone Postgres. Prefer your existing Postgres on port **5433**. |
| `pytest.ini` | Sets `pythonpath = .` so tests can `import app`. |

### `app/config/settings.py`

- Reads environment variables with `pydantic-settings`
- Exposes: Gemini key, model name, LangSmith flags, `DATABASE_URL`
- Default DB: `postgresql+psycopg2://postgres:postgres@localhost:5433/travel_agent`

### `app/database/connection.py`

- Parses `DATABASE_URL` into host/port/user/password/dbname
- `get_connection()` → open a `psycopg2` connection
- `connection_scope()` → commit on success, rollback on error, then close

### `app/database/schema.py`

- Contains the full **DDL** (`CREATE TABLE IF NOT EXISTS ...`)
- Three tables: `flights`, `hotels`, `bookings`
- No ORM models — schema is plain SQL string `SCHEMA_SQL`

### `app/database/repository.py`

- Only place that runs SQL (`INSERT`, `SELECT`, `UPDATE`)
- Methods like `add_flight`, `get_flights`, `create_booking`, `cancel_booking`
- Returns Python `dict` rows (via `RealDictCursor`)

### Services (business logic)

| File | Functions | Role |
|------|-----------|------|
| `flight_service.py` | `add_flight`, `get_flights` | Ingest & search flights |
| `hotel_service.py` | `add_hotel`, `get_hotels` | Ingest & search hotels |
| `booking_service.py` | `book_flight`, `book_hotel`, `cancel_booking` | Booking rules + inventory updates |

Services call the repository inside `connection_scope()`.  
They do **not** talk to Gemini.

### Tools (LLM-callable)

| File | Tools | Role |
|------|-------|------|
| `flight_tools.py` | `get_flights` | Agent searches flights |
| `hotel_tools.py` | `get_hotels` | Agent searches hotels |
| `booking_tools.py` | `book_flight`, `book_hotel`, `cancel_booking` | Agent books/cancels |

Each `@tool` is a thin wrapper around a service function and returns text/JSON for the model.

### Agent

| File | Role |
|------|------|
| `prompts.py` | Tells Gemini: use tools, don’t invent flight numbers/prices, ask clarifying questions |
| `travel_agent.py` | Creates `ChatGoogleGenerativeAI`, registers tools, returns `create_agent(...)` |

### Entry points

| File | Role |
|------|------|
| `app/main.py` | Interactive chat loop: read input → `agent.invoke` → print answer |
| `app/api/routes.py` | Optional HTTP API for search/book/cancel without the LLM |
| `app/data/seed_data.py` | Sample inventory used by the seed script |

### Scripts

| Script | What it does |
|--------|----------------|
| `scripts/ensure_db.py` | Connects to Postgres DB `postgres`, runs `CREATE DATABASE travel_agent` if needed |
| `scripts/init_db.py` | Calls `ensure_db`, then executes `SCHEMA_SQL` to create tables |
| `scripts/seed_demo_data.py` | Inserts demo flights/hotels using `add_flight` / `add_hotel` (skips duplicates) |

---

## 5. Database — create everything from scratch

### 5.1 Prerequisites

You need PostgreSQL reachable at:

```text
Host: localhost
Port: 5433
User: postgres
Password: postgres
```

(This matches the existing `pgvector-db` style setup used in this repo.)

Confirm it is up, then create the app database and tables.

### 5.2 Connection string

In `.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/travel_agent
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=travel_agent
POSTGRES_PORT=5433
```

Meaning:

| Part | Value | Meaning |
|------|-------|---------|
| Driver | `postgresql+psycopg2` | Use `psycopg2` (parsed to a normal Postgres DSN) |
| User / password | `postgres` / `postgres` | Login |
| Host / port | `localhost:5433` | Your local Postgres |
| Database name | `travel_agent` | Dedicated DB for this app |

### 5.3 Step A — create the database

```bash
cd travel_agent
python scripts/ensure_db.py
```

What happens internally:

1. Connect to the default `postgres` database
2. Check if `travel_agent` exists
3. If not: `CREATE DATABASE "travel_agent"`

Or run it as part of init (recommended):

```bash
python scripts/init_db.py
```

`init_db.py` calls `ensure_database()` first, then creates tables.

### 5.4 Step B — create tables

```bash
python scripts/init_db.py
```

This runs SQL from `app/database/schema.py` and creates:

#### Table: `flights`

| Column | Type | Notes |
|--------|------|--------|
| `id` | SERIAL PK | Auto id |
| `flight_number` | VARCHAR | e.g. `AI202` |
| `airline` | VARCHAR | e.g. Air India |
| `origin` / `destination` | VARCHAR | Cities |
| `departure_date` | DATE | Travel day |
| `departure_time` / `arrival_time` | VARCHAR | e.g. `06:30` |
| `price` | DOUBLE | Ticket price |
| `seats_available` | INTEGER | Inventory |
| `created_at` | TIMESTAMPTZ | Default `NOW()` |

Unique constraint: `(flight_number, departure_date)`  
Indexes on origin, destination, date, flight_number.

#### Table: `hotels`

| Column | Type | Notes |
|--------|------|--------|
| `id` | SERIAL PK | Used when booking (`Book hotel 1 ...`) |
| `name` | VARCHAR | Hotel name |
| `city` | VARCHAR | Search key |
| `address` | VARCHAR | Optional |
| `stars` | INTEGER | Rating |
| `price_per_night` | DOUBLE | Nightly rate |
| `rooms_available` | INTEGER | Inventory |
| `amenities` | TEXT | Free text |
| `created_at` | TIMESTAMPTZ | Default `NOW()` |

#### Table: `bookings`

| Column | Type | Notes |
|--------|------|--------|
| `id` | SERIAL PK | Internal id |
| `booking_id` | VARCHAR UNIQUE | Public id like `BK-A1B2C3D4E5` |
| `booking_type` | VARCHAR | `flight` or `hotel` |
| `customer_name` | VARCHAR | Passenger / guest |
| `reference` | VARCHAR | Flight number or hotel id |
| `details` | TEXT | Human-readable summary |
| `check_in` / `check_out` | DATE | Hotel stays only |
| `total_price` | DOUBLE | Charged amount |
| `status` | VARCHAR | `confirmed` or `cancelled` |
| `created_at` | TIMESTAMPTZ | Default `NOW()` |

### 5.5 Verify in Postgres (optional)

```sql
\c travel_agent
\dt
SELECT COUNT(*) FROM flights;
SELECT COUNT(*) FROM hotels;
SELECT * FROM bookings LIMIT 5;
```

---

## 6. How to ingest data (flights & hotels)

Inventory must exist **before** bookings work.

### Method 1 — seed script (recommended first time)

1. Edit sample rows in `app/data/seed_data.py` (`DEMO_FLIGHTS`, `DEMO_HOTELS`)
2. Run:

```bash
python scripts/seed_demo_data.py
```

The script:

- Checks if the flight/hotel already exists
- Skips duplicates
- Calls `add_flight(...)` / `add_hotel(...)` for new rows

### Method 2 — Python `add_flight()` / `add_hotel()`

From the `travel_agent` folder (or with that folder on `PYTHONPATH`):

```python
from app.services.flight_service import add_flight
from app.services.hotel_service import add_hotel

add_flight(
    flight_number="AI501",
    airline="Air India",
    origin="Hyderabad",
    destination="Mumbai",
    departure_date="2026-10-15",
    departure_time="07:00",
    arrival_time="08:30",
    price=4100.0,
    seats_available=20,
)

add_hotel(
    name="Airport Inn",
    city="Delhi",
    address="Aerocity",
    stars=4,
    price_per_night=5500.0,
    rooms_available=10,
    amenities="WiFi, Breakfast",
)
```

### What ingestion does in SQL

`add_flight` ultimately runs something like:

```sql
INSERT INTO flights (
  flight_number, airline, origin, destination,
  departure_date, departure_time, arrival_time,
  price, seats_available
) VALUES (...);
```

Same idea for hotels into the `hotels` table.

---

## 7. How bookings work

### Create a flight booking

**CLI (natural language)**

```text
Book flight AI202 for Madhu
```

**Python**

```python
from app.services.booking_service import book_flight

book_flight("AI202", "Madhu", departure_date="2026-10-10")
```

**Internal steps**

1. Find flight by number (and optional date)
2. Check `seats_available >= 1`
3. `UPDATE flights SET seats_available = seats_available - 1`
4. Insert row into `bookings` with a new `BK-...` id
5. Return booking details

### Create a hotel booking

```text
Book hotel 1 for Madhu from 2026-10-10 to 2026-10-12
```

```python
from app.services.booking_service import book_hotel

book_hotel(1, "Madhu", "2026-10-10", "2026-10-12")
```

Price = `price_per_night * number_of_nights`.  
Rooms available is decremented by 1.

### Cancel a booking

```text
Cancel booking BK-XXXXXXXXXX
```

```python
from app.services.booking_service import cancel_booking

cancel_booking("BK-XXXXXXXXXX")
```

Sets `status = 'cancelled'` and restores seats/rooms.

---

## 8. Full local run (end-to-end checklist)

```bash
# 1) Enter project
cd travel_agent

# 2) Virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3) Install dependencies
pip install -r requirements.txt

# 4) Configure secrets
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux
# Edit .env → set GEMINI_API_KEY (or GOOGLE_API_KEY)
# Confirm DATABASE_URL points to localhost:5433/travel_agent
# Confirm GEMINI_MODEL=gemini-3.8-flash

# 5) Create database + tables
python scripts/init_db.py

# 6) Load demo inventory
python scripts/seed_demo_data.py

# 7) Start chat agent
python app/main.py
```

### Example chat

```text
Find flights from Hyderabad to Delhi on 2026-10-10
Find hotels in Delhi
Book flight AI202 for Madhu
Book hotel 1 for Madhu from 2026-10-10 to 2026-10-12
Cancel booking BK-XXXXXXXXXX
```

Type `exit`, `quit`, or `bye` to leave.

---

## 9. Optional: HTTP API (no chat)

```bash
uvicorn app.api.routes:app --reload
```

Useful routes (see `app/api/routes.py`):

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| POST | `/flights/search` | Search flights |
| POST | `/hotels/search` | Search hotels |
| POST | `/bookings/flight` | Book a flight |
| POST | `/bookings/hotel` | Book a hotel |
| POST | `/bookings/cancel` | Cancel a booking |

These call the **same services** as the agent tools.

---

## 10. Tests

```bash
pytest tests/ -q
```

`tests/test_repository.py` inserts temporary rows into your real Postgres `travel_agent` DB, asserts SQL behavior, then deletes those test rows.

---

## 11. Environment variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `GEMINI_API_KEY` or `GOOGLE_API_KEY` | Gemini auth | your key |
| `GEMINI_MODEL` | Model id | `gemini-3.8-flash` |
| `LANGCHAIN_TRACING_V2` | LangSmith on/off | `true` / `false` |
| `LANGCHAIN_API_KEY` | LangSmith key | optional |
| `LANGCHAIN_PROJECT` | LangSmith project name | `travel-agent` |
| `DATABASE_URL` | Postgres connection | see section 5.2 |

---

## 12. Design notes (important)

1. **Layering**  
   Agent → Tools → Services → Repository → Postgres  
   Keep SQL in `repository.py` only.

2. **No ORM**  
   Tables are created with plain SQL in `schema.py`. Queries use `psycopg2`.

3. **Simulated inventory**  
   Good for learning agents + tools + DB. Not live airline/hotel data.

4. **Same Postgres, local app**  
   The Python process runs on your machine; only the DB is the existing Postgres on port `5433`.

5. **Extending later**  
   To use real flight/hotel APIs, replace service/repository implementations. Keep tool names and agent prompt mostly unchanged.

---

## 13. Quick troubleshooting

| Problem | Fix |
|---------|-----|
| `model ... gemini-2.0-flash is no longer available` | Set `GEMINI_MODEL=gemini-3.8-flash` in `.env` |
| Missing API key | Set `GEMINI_API_KEY` or `GOOGLE_API_KEY` in `.env` |
| Connection refused on 5433 | Start your Postgres / `pgvector-db` container |
| No flights found | Run `python scripts/seed_demo_data.py` |
| Booking fails / no seats | Seed data first; check `seats_available` / `rooms_available` |
| Import errors when running scripts | Run commands from the `travel_agent` folder |

---

## 14. One-page mental model

```text
.create DB + tables     →  scripts/init_db.py
.load flights/hotels    →  scripts/seed_demo_data.py  OR  add_flight()/add_hotel()
.chat / book / cancel   →  python app/main.py
.optional REST          →  uvicorn app.api.routes:app --reload
.all data lives in      →  PostgreSQL database: travel_agent
```
