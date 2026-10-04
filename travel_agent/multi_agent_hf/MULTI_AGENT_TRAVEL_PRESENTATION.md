# Multi-Agent Orchestration with Travel Agent (Hugging Face Local)

**Focus:** Sequential Workflow and Supervisor Workflow  
**Package:** `travel_agent/multi_agent_hf/`  
**Stack:** Python · LangGraph · Hugging Face local model · Postgres inventory (with seed fallback)

> Companion walkthrough with step-by-step run order: [`EXECUTION_GUIDE.md`](EXECUTION_GUIDE.md)  
> Gemini version (separate package): `travel_agent/multi_agent/`

---

## Two packages in this project

| Folder | Model | When to use |
|---|---|---|
| `multi_agent/` | Google Gemini | Cloud LLM, tool-calling demos |
| `multi_agent_hf/` | Hugging Face **local** | No Gemini / no HF token / offline-friendly demos |

This document is for **`multi_agent_hf/`**.

---

## Setup

```bash
cd travel_agent
pip install -r requirements.txt
pip install -r requirements-hf.txt
```

If torch is heavy on Windows CPU:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers accelerate huggingface_hub
```

### Model setting (one place only)

```python
# multi_agent_hf/llm.py
HF_MODE = "local"   # no HF token required
HF_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# HF_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"  # smaller/faster
```

Optional `.env` values (mainly for Postgres / LangSmith):

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=travel-agent
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/travel_agent
# HF_TOKEN=   # only needed if you later switch HF_MODE = "api"
```

### Inventory setup (optional but recommended)

```bash
docker compose --profile standalone up -d
python scripts/init_db.py
python scripts/seed_demo_data.py
```

If Docker Desktop fails, continue anyway. Flight/Hotel agents fall back to `app/data/seed_data.py`.

Useful inventory dates:

```text
Hyderabad -> Delhi on 2026-10-10
Hyderabad -> Delhi on 2026-04-15
Hotels in Delhi / Mumbai / Hyderabad
```

---

## 1. What we are building

Progressive travel system:

```text
Single Agent
    → Specialized Agents
    → Sequential Workflow
    → Supervisor Workflow
```

### Core travel request

```text
"Book me a flight from Hyderabad to Delhi,
find a hotel near the airport,
and prepare my itinerary."
```

One agent can try this alone. A better design splits responsibilities.

### Target sequential architecture

```text
                    USER QUERY
                        |
                        v
              +-------------------+
              |   Flight Agent    |
              +---------+---------+
                        |
                        v
              +-------------------+
              |   Hotel Agent     |
              +---------+---------+
                        |
                        v
              +-------------------+
              | Itinerary Agent   |
              +---------+---------+
                        |
                        v
                  FINAL PLAN
```

### Target supervisor architecture

```text
                       USER
                        |
                        v
                +---------------+
                |   SUPERVISOR  |
                +-------+-------+
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
       Flight         Hotel       Itinerary
        Agent         Agent         Agent
          |             |             |
          +-------------+-------------+
                        |
                        v
                   SUPERVISOR
                        |
                        v
                    FINAL PLAN
```

### Quick terms

| Term | Meaning |
|---|---|
| Agent | Performs one responsibility |
| Workflow | Defines how agents are connected |
| Supervisor | Decides which worker runs next |
| Worker agent | Specialist that does the actual work |
| Shared state | Common workspace for intermediate results |
| Inventory | Real flights/hotels from Postgres or seed data |

### Why not one giant travel agent?

- Harder to control quality
- Harder to debug
- Tools/data access get mixed
- Responsibilities overlap
- One bad step pollutes the whole answer

### How this HF package stays factual

```text
trip_parse.py     → extract origin/destination/date (Python)
inventory.py      → Postgres first, else seed_data
flight/hotel agents → format real rows
supervisor        → rule-based routing (reliable on small local models)
```

Small local models are **not** used to invent flight numbers or hotel prices.

---

## 2. Single-agent baseline

Run:

```bash
python multi_agent_hf/examples/01_single_agent_baseline.py
```

### Example prompts

```text
Book me a flight from Hyderabad to Delhi, find a hotel near the airport, and prepare my itinerary for 3 days.
```

```text
Plan a weekend trip from Bangalore to Goa with flight, beach hotel, and day-wise plan.
```

### What to highlight

This baseline has **no database access**.

You may see generic advice like “go to the airline website”.  
That is expected — and exactly why specialists + inventory matter.

Also run:

```bash
python multi_agent_hf/examples/07_bad_vs_good_boundaries.py
```

---

## 3. Specialized travel agents

Development rule:

```text
Agent Development
       ↓
Independent Testing
       ↓
Orchestration
```

### 3.1 Flight Agent

**Responsibility**

```text
Input:  travel request
Output: flight findings from inventory
```

**Does**

- parse origin, destination, date (Python)
- look up flights in Postgres/seed
- recommend from real options

**Does not**

- choose hotels
- invent flight numbers
- write the final itinerary

Run:

```bash
python -m multi_agent_hf.agents.flight_agent
```

#### Flight examples

```text
Find flights from Hyderabad to Delhi on 2026-10-10 for a 3-day business trip.
```

```text
Only research flights from Hyderabad to Delhi on 2026-04-15.
```

```text
Show evening flights from Hyderabad to Delhi on 2026-10-10.
```

Expected style:

```text
Flight findings (FROM INVENTORY — not model invention)
Source: postgres   OR   seed_data (...)
Lookup: Hyderabad -> Delhi on 2026-10-10
Found 3 flight(s):
1. AI202 - Air India ...
Recommendation (from inventory): 6E451 ...
```

### 3.2 Hotel Agent

**Responsibility**

```text
Input:  travel request + optional flight findings
Output: hotel findings from inventory
```

**Does**

- detect destination city
- query hotels
- prefer airport hotel when request mentions airport

**Does not**

- search flights
- invent hotel names/prices

#### Hotel examples

```text
I need a hotel near the airport in Delhi for 3 nights.
```

```text
Find a 4-star hotel in Delhi close to the airport.
```

```text
Suggest budget hotels in Delhi for a 3-day trip.
```

### 3.3 Itinerary Agent

**Responsibility**

```text
Input:  request + flight findings + hotel findings
Output: grounded final travel plan
```

It uses the recommendations already produced by Flight/Hotel agents.  
It should not invent new inventory facts.

#### Itinerary examples

```text
Create a 3-day Delhi business itinerary using the selected flight and airport hotel.
```

```text
Build a relaxed 2-day plan around the recommended arrival and hotel.
```

### Test all three independently

```bash
python multi_agent_hf/examples/02_unit_test_each_agent.py
```

Mixed prompts:

```text
Flight Hyderabad -> Delhi on 2026-10-10, hotel near airport, 3-day trip.
```

```text
Flight Hyderabad -> Delhi on 2026-04-15, hotel near airport, 3-day trip.
```

```text
Hyderabad to Delhi early flight, city hotel, 2-day plan.
```

---

## 4. Shared state

Agents collaborate through a shared workspace.

Run:

```bash
python multi_agent_hf/examples/03_shared_state_demo.py
```

### State shape

```python
class TravelState(TypedDict):
    request: str
    flights: str
    hotels: str
    itinerary: str
    final_answer: str
```

### How state evolves

**Initial**

```text
request = user question
flights = empty
hotels = empty
itinerary = empty
final_answer = empty
```

**After Flight Agent**

```text
flights = inventory findings
```

**After Hotel Agent**

```text
hotels = inventory findings
```

**After Itinerary Agent**

```text
itinerary = plan
final_answer = plan
```

### Why state matters

Without shared state:

```text
Flight Agent: "I found 6E451 morning flight."
Hotel Agent:  "Which city? What arrival time?"
```

With shared state:

```text
Flight Agent writes findings into state
Hotel Agent reads destination/context
Hotel recommendation becomes trip-aware
```

Also run:

```bash
python multi_agent_hf/examples/08_handoff_and_state.py
```

---

## 5. Sequential workflow

Fixed order:

```text
Flight Agent
      ↓
Hotel Agent
      ↓
Itinerary Agent
```

This fits travel planning when you always:

1. choose travel
2. then stay
3. then build the day plan

### LangGraph building blocks

| Concept | In this project |
|---|---|
| State | `TravelState` |
| Node | `flight_node`, `hotel_node`, `itinerary_node` |
| Edge | flight → hotel → itinerary |
| Boundaries | START → ... → END |

```text
START
  |
  v
Flight
  |
  v
Hotel
  |
  v
Itinerary
  |
  v
END
```

### Run sequential

```bash
python -m multi_agent_hf.main sequential
python multi_agent_hf/examples/04_sequential_demo.py
```

Custom query:

```bash
python -m multi_agent_hf.main sequential --query "Plan Hyderabad to Delhi on 2026-10-10 with airport hotel and itinerary"
```

### Live demo queries

**Full trip**

```text
Plan a trip from Hyderabad to Delhi on 2026-10-10: find a flight, a hotel near the airport, and prepare a 3-day itinerary.
```

**Business trip**

```text
Plan a business trip from Hyderabad to Delhi on 2026-04-15 with airport hotel and meeting-friendly timings.
```

**Budget trip**

```text
Plan a budget 3-day Delhi trip from Hyderabad focusing on low hotel cost.
```

### What to inspect after each run

```text
Input
 ↓
Flight output (Source: postgres / seed_data)
 ↓
Hotel output
 ↓
Itinerary / final answer
```

Check whether:

- hotel city matches flight destination
- recommendation uses real inventory
- itinerary references those recommendations

Open:

```text
multi_agent_hf/workflows/sequential_workflow.py
```

---

## 6. Observability and failure modes

If LangSmith is configured, inspect traces under project `travel-agent-hf` (or your configured name).

Ideal shape:

```text
Workflow
│
├── Flight Agent
│     ├── trip parse
│     ├── inventory lookup
│     └── formatted findings
│
├── Hotel Agent
│     ├── city detect
│     ├── inventory lookup
│     └── formatted findings
│
└── Itinerary Agent
      └── grounded plan
```

### Failure mode examples

**1. Bad field parsing (old design)**

```text
Small LLM invents origin/destination JSON
  → DB lookup skipped
  → fake flights appear
```

Current HF design avoids this with Python parsing + inventory.

**2. Wrong date**

```text
Request uses 2026-05-01
Inventory has 2026-10-10 / 2026-04-15
  → no flights found
```

**3. Responsibility overlap**

```text
Flight Agent also recommends hotels
Hotel Agent becomes unclear
```

**4. Docker/Postgres down**

```text
Source: seed_data (postgres unavailable...)
```

Orchestration still works. Inventory still real (from seed).

**5. Context overload**

```text
Huge raw JSON dumped into every prompt
  → noisy for LLM stages
```

Keep summaries clean; keep raw JSON optional at the end.

---

## 7. Why sequential is not always enough

Sequential always does:

```text
Flight → Hotel → Itinerary
```

But real requests vary.

### Example A — flight only

```text
"Only research flights from Hyderabad to Delhi on 2026-04-15."
```

Hotel and itinerary may be unnecessary.

### Example B — hotel only

```text
"Find hotels near Delhi airport for 3 nights."
```

No flight search needed.

### Example C — full trip

```text
"Plan full trip: Hyderabad to Delhi on 2026-04-15, airport hotel, and prepare itinerary."
```

Needs all three workers.

### Router vs Supervisor

Run:

```bash
python multi_agent_hf/examples/06_router_vs_supervisor.py
```

| Pattern | Behavior |
|---|---|
| Router | Choose one specialist, often stop |
| Supervisor | Choose next worker, repeat until FINISH |

```text
Router:
"Which one agent should handle this?"

Supervisor:
"Which agent should work next, and are we done yet?"
```

---

## 8. Supervisor workflow

Architecture:

```text
                 Supervisor
                /     |     \
               /      |      \
              v       v       v
           Flight   Hotel  Itinerary
              \      |      /
               \     |     /
                Supervisor
                     |
                     v
                   END
```

Supervisor decides one of:

```text
flight
hotel
itinerary
FINISH
```

### Mental model

```text
Sequential:
"I already know the order."

Supervisor:
"I need logic to decide the order."
```

### Local HF note

TinyLlama is weak at returning only `flight|hotel|itinerary|FINISH`.  
In `multi_agent_hf`, supervisor routing is **rule-based** so demos stay correct.  
Workers still use inventory-backed agents.

### Run supervisor

```bash
python -m multi_agent_hf.main supervisor
python multi_agent_hf/examples/05_supervisor_demo.py
python multi_agent_hf/examples/09_supervisor_routing_cases.py
```

Custom:

```bash
python -m multi_agent_hf.main supervisor --query "Only research flights from Hyderabad to Delhi on 2026-04-15."
```

### Routing examples

**Case 1 — flight only**

```text
Only research flights from Hyderabad to Delhi on 2026-04-15.
```

Expected path:

```text
supervisor → flight → supervisor → FINISH
```

**Case 2 — hotel only**

```text
Find hotels near the airport in Delhi for 3 nights.
```

Expected path:

```text
supervisor → hotel → supervisor → FINISH
```

**Case 3 — full trip**

```text
Plan full trip: Hyderabad to Delhi on 2026-04-15, airport hotel, and prepare itinerary.
```

Expected path:

```text
supervisor → flight → hotel → itinerary → FINISH
```

**Case 4 — constrained request**

```text
Find only morning flights HYD to DEL. Do not plan hotel.
```

Expected path:

```text
supervisor → flight → FINISH
```

### Safety

```text
MAX_STEPS guard prevents infinite supervisor loops
```

Open:

```text
multi_agent_hf/workflows/supervisor_workflow.py
```

---

## 9. Sequential vs Supervisor

| Sequential Workflow | Supervisor Workflow |
|---|---|
| Fixed execution order | Dynamic execution |
| A → B → C | Supervisor → Agent → Supervisor |
| Simple | More flexible |
| Predictable | Decision-based |
| Good for pipelines | Good for mixed intents |
| Lower orchestration complexity | Higher orchestration complexity |
| Every step usually runs | Only needed steps may run |
| Best for fixed travel packages | Best for varying travel requests |

### Same domain, two interpretations

```text
Sequential always runs full package planning.
Supervisor can stop after flight-only research.
```

Run both:

```bash
python -m multi_agent_hf.main both --query "Plan Hyderabad to Delhi on 2026-10-10 with airport hotel and itinerary"
```

---

## 10. Parallel concept (preview)

Independent travel tasks can also run in parallel:

```text
Travel Request
      |
      ├─ Flight Agent
      ├─ Hotel Agent
      └─ Activities Agent
      |
      v
Itinerary Agent
```

Run:

```bash
python multi_agent_hf/examples/10_parallel_travel_concept.py
```

Contrast:

```text
Sequential: hotel waits for flight
Parallel: flight and hotel can start together when independent
Supervisor: decides what is needed based on the request
```

---

## 11. More presentation examples by theme

### Theme A — City pairs / dates in inventory

```text
Hyderabad → Delhi (2026-10-10)
Hyderabad → Delhi (2026-04-15)
Delhi hotels near airport
Mumbai hotels
Hyderabad hotels
```

### Theme B — Intent types

```text
Flight-only research
Hotel-only search
Full trip package
Itinerary from prior findings
Budget optimization
Business meeting trip
```

### Theme C — Constraint language

```text
"near airport"
"under INR 5000"
"morning flight only"
"3 days only"
"no hotel needed"
"only research flights"
```

### Theme D — Predicted supervisor routes

Before running, predict the path:

```text
1) "Research flights Hyderabad to Delhi."
   → flight → FINISH

2) "Find airport hotels in Delhi."
   → hotel → FINISH

3) "Plan my full Delhi trip from Hyderabad."
   → flight → hotel → itinerary → FINISH
```

Then run and compare against `Steps:`.

---

## 12. Extension ideas

### Extension 1 — Booking Agent in sequential

```text
Flight → Hotel → Itinerary → Booking
```

Booking Agent should:

- book only chosen flight/hotel
- not re-search everything
- return booking IDs clearly

### Extension 2 — Policy Checker in supervisor

```text
Supervisor
  ├── Flight
  ├── Hotel
  ├── Policy Checker
  └── Itinerary
```

Policy Checker can validate:

- budget limits
- cancellation windows
- ID / travel document reminders
- company travel policy rules

### Extension 3 — Switch model size

In `multi_agent_hf/llm.py`:

```python
HF_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# HF_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
```

Inventory-backed Flight/Hotel quality stays the same because those agents do not invent inventory.

---

## 13. End-to-end picture

```text
                 MULTI-AGENT TRAVEL (HF LOCAL)
                              |
               +--------------+--------------+
               |                             |
               v                             v
       SEQUENTIAL WORKFLOW           SUPERVISOR WORKFLOW
               |                             |
               v                             v
        Flight Agent                   Supervisor
               |                       /    |    \
               v                      /     |     \
        Hotel Agent              Flight  Hotel  Itinerary
               |                      \      |      /
               v                       \     |     /
       Itinerary Agent                Supervisor
               |                           |
               v                           v
          Final Plan                     END
```

### Data path

```text
User request
  → trip_parse.py
  → inventory.py
      → Postgres (if up)
      → else seed_data.py
  → Flight / Hotel findings
  → Itinerary (grounded)
```

### Concepts covered

```text
Python
 → Hugging Face local model
 → LangGraph
 → Specialized Agents
 → Shared State
 → Nodes and Edges
 → Sequential Workflow
 → Supervisor Workflow
 → Inventory grounding (Postgres / seed)
 → Observability mindset
```

### Key takeaway

```text
Sequential: "I already know the order."
Supervisor: "I need logic to decide the order."
Inventory:  "Workers must use real data, not hallucinations."
```

---

## 14. Suggested run order

```bash
cd travel_agent

# A. Concepts
python multi_agent_hf/examples/07_bad_vs_good_boundaries.py
python multi_agent_hf/examples/03_shared_state_demo.py
python multi_agent_hf/examples/08_handoff_and_state.py
python multi_agent_hf/examples/06_router_vs_supervisor.py
python multi_agent_hf/examples/10_parallel_travel_concept.py

# B. Baseline vs specialists
python multi_agent_hf/examples/01_single_agent_baseline.py
python multi_agent_hf/examples/02_unit_test_each_agent.py

# C. Orchestration
python multi_agent_hf/examples/04_sequential_demo.py
python multi_agent_hf/examples/05_supervisor_demo.py
python multi_agent_hf/examples/09_supervisor_routing_cases.py

# D. Combined
python -m multi_agent_hf.main both
```

---

## 15. Command cheat sheet

```bash
cd travel_agent

# setup
pip install -r requirements.txt
pip install -r requirements-hf.txt
python scripts/init_db.py
python scripts/seed_demo_data.py

# concept demos
python multi_agent_hf/examples/01_single_agent_baseline.py
python multi_agent_hf/examples/03_shared_state_demo.py
python multi_agent_hf/examples/06_router_vs_supervisor.py
python multi_agent_hf/examples/07_bad_vs_good_boundaries.py
python multi_agent_hf/examples/08_handoff_and_state.py
python multi_agent_hf/examples/10_parallel_travel_concept.py

# specialists
python multi_agent_hf/examples/02_unit_test_each_agent.py
python -m multi_agent_hf.agents.flight_agent
python -m multi_agent_hf.agents.hotel_agent
python -m multi_agent_hf.agents.itinerary_agent

# orchestration
python -m multi_agent_hf.main sequential
python -m multi_agent_hf.main supervisor
python -m multi_agent_hf.main both
python multi_agent_hf/examples/04_sequential_demo.py
python multi_agent_hf/examples/05_supervisor_demo.py
python multi_agent_hf/examples/09_supervisor_routing_cases.py
```

### If local HF model is slow / downloading

Use concept demos first:

```bash
python multi_agent_hf/examples/03_shared_state_demo.py
python multi_agent_hf/examples/06_router_vs_supervisor.py
python multi_agent_hf/examples/07_bad_vs_good_boundaries.py
python multi_agent_hf/examples/08_handoff_and_state.py
python multi_agent_hf/examples/10_parallel_travel_concept.py
python multi_agent_hf/examples/02_unit_test_each_agent.py
```

`02` is inventory-backed and does not need a strong LLM for flight/hotel facts.

### If Postgres / Docker is down

Continue. You will see:

```text
Source: seed_data (postgres unavailable...)
```

That still uses real demo inventory from `app/data/seed_data.py`.

```text
Data plane can fall back
Orchestration plane still runs
```

### If you want Gemini instead

Use the sibling package:

```bash
python -m multi_agent.main sequential
```

Model for Gemini is set in:

```python
# app/config/settings.py
GEMINI_MODEL = "..."
```

---

## 16. Project file map

```text
travel_agent/multi_agent_hf/
├── MULTI_AGENT_TRAVEL_PRESENTATION.md   ← this file
├── EXECUTION_GUIDE.md                   ← start-to-end run guide
├── README.md
├── llm.py                               ← HF_MODEL / HF_MODE
├── trip_parse.py                        ← Python field extraction
├── inventory.py                         ← Postgres first, seed fallback
├── main.py
├── agents/
│   ├── flight_agent.py
│   ├── hotel_agent.py
│   └── itinerary_agent.py
├── workflows/
│   ├── state.py
│   ├── sequential_workflow.py
│   └── supervisor_workflow.py
└── examples/
    ├── 01_single_agent_baseline.py
    ├── 02_unit_test_each_agent.py
    ├── 03_shared_state_demo.py
    ├── 04_sequential_demo.py
    ├── 05_supervisor_demo.py
    ├── 06_router_vs_supervisor.py
    ├── 07_bad_vs_good_boundaries.py
    ├── 08_handoff_and_state.py
    ├── 09_supervisor_routing_cases.py
    └── 10_parallel_travel_concept.py
```
