# Multi-Agent Orchestration with Travel Agent

**Focus:** Sequential Workflow and Supervisor Workflow  
**Project:** Multi-Agent Travel Planner in `travel_agent/`  
**Stack:** Python · LangChain · LangGraph · Google Gemini · LangSmith · Postgres inventory

---

## Setup

```bash
cd travel_agent
pip install -r requirements.txt
```

Make sure `.env` has API keys / DB settings:

```env
GOOGLE_API_KEY=your_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=travel-agent
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/travel_agent
```

Set the model name in **one place only**:

```python
# app/config/settings.py
GEMINI_MODEL = "gemini-2.5-flash"
```

Optional inventory setup:

```bash
python scripts/init_db.py
python scripts/seed_demo_data.py
```

---



## 1. What we are building

We already know multi-agent theory. Now we build one progressive travel system:

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
                ┌───────────────┐
                │   SUPERVISOR  │
                └───────┬───────┘
                        |
          ┌─────────────┼─────────────┐
          |             |             |
          v             v             v
       Flight         Hotel       Itinerary
        Agent         Agent         Agent
          |             |             |
          └─────────────┼─────────────┘
                        |
                        v
                   SUPERVISOR
                        |
                        v
                    FINAL PLAN
```



### Quick terms


| Term         | Meaning                                   |
| ------------ | ----------------------------------------- |
| Agent        | Performs one responsibility               |
| Workflow     | Defines how agents are connected          |
| Supervisor   | Decides which worker runs next            |
| Worker agent | Specialist that does the actual work      |
| Shared state | Common workspace for intermediate results |




### Why not one giant travel agent?

- Harder to control quality
- Harder to debug
- Tools get mixed (flight + hotel + booking)
- Responsibilities overlap
- One bad step pollutes the whole answer

---



## 2. Single-agent baseline

Run:

```bash
python multi_agent/examples/01_single_agent_baseline.py
```



### Example prompts to show live

```text
Book me a flight from Hyderabad to Delhi, find a hotel near the airport, and prepare my itinerary for 3 days.
```

```text
Plan a weekend trip from Bangalore to Goa with flight, beach hotel, and day-wise plan.
```

```text
I need a cheap Hyderabad to Mumbai morning flight, a 3-star hotel, and a simple 2-day plan.
```



### What to highlight

The single agent may answer, but:

- flight search, hotel selection, and itinerary writing are mixed
- debugging is hard because everything happens in one blob
- we cannot reuse only the hotel specialist later

That is why we create specialists.

Also run the boundary demo:

```bash
python multi_agent/examples/07_bad_vs_good_boundaries.py
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
Output: flight findings
```

**Does**

- extract origin, destination, date
- look up / summarize flight options
- recommend practical flight choices

**Does not**

- choose hotels
- write the final itinerary
- invent bookings

Run:

```bash
python -m multi_agent.agents.flight_agent
```



#### Flight examples

```text
Find flights from Hyderabad to Delhi on 2026-04-15 for a 3-day business trip.
```

```text
I need the cheapest morning flight from Bangalore to Chennai next Monday.
```

```text
Show me evening flights from Hyderabad to Mumbai under ₹6000.
```

```text
Compare early morning vs late night flights HYD → DEL for a same-day meeting.
```

Expected style of output:

```text
Flight Findings
---------------
Route: Hyderabad → Delhi
Date: 2026-04-15
Options:
1. Morning flight — better for business day
2. Evening flight — lower rush, later arrival
Recommendation: ...
```



### 3.2 Hotel Agent

**Responsibility**

```text
Input:  travel request + optional flight findings
Output: hotel findings
```

**Does**

- identify destination city
- summarize hotel options
- prefer airport / city-center based on request

**Does not**

- search flights
- create day-by-day itinerary



#### Hotel examples

```text
I need a hotel near the airport in Delhi for 3 nights starting 2026-04-15.
```

```text
Find a 4-star hotel in Mumbai close to the airport with easy late check-in.
```

```text
Suggest budget hotels in Goa near the beach, not near the airport.
```

```text
Based on a 9 PM Delhi arrival, which hotel makes sense?
```

Expected style:

```text
Hotel Findings
--------------
City: Delhi
Preference: near airport
Options:
1. Airport 4-star — shorter transfer
2. City center 3-star — cheaper, longer commute
Recommendation: ...
```



### 3.3 Itinerary Agent

**Responsibility**

```text
Input:  request + flight findings + hotel findings
Output: reviewed final travel plan
```

Checks:

- completeness
- timing conflicts
- missing information
- unsupported claims
- clear day-by-day structure



#### Itinerary examples

```text
Create a 3-day Delhi business itinerary using the selected morning flight and airport hotel.
```

```text
Build a relaxed 2-day Goa plan around afternoon arrival and a beach hotel.
```

```text
Review this trip plan and point out missing information before finalizing.
```

Expected style:

```text
Final Itinerary
---------------
Trip overview
Recommended flight
Recommended hotel
Day 1 / Day 2 / Day 3
Assumptions / open questions
```



### Test all three independently

```bash
python multi_agent/examples/02_unit_test_each_agent.py
```

More mixed prompts for independent testing:

```text
Flight Hyderabad → Delhi on 2026-04-15, hotel near airport, 3-day trip.
```

```text
Bangalore to Goa Friday evening flight, beach hotel, weekend itinerary.
```

```text
Hyderabad to Chennai early flight, city hotel near office area, 2-day plan.
```

---



## 4. Shared state

Agents collaborate through a shared workspace.

Run:

```bash
python multi_agent/examples/03_shared_state_demo.py
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
flights = flight output
```

**After Hotel Agent**

```text
hotels = hotel output
```

**After Itinerary Agent**

```text
itinerary = plan
final_answer = plan
```



### Travel example of why state matters

Without shared state:

```text
Flight Agent: "I found HYD-DEL morning flight."
Hotel Agent:  "Which city? What arrival time?"
```

With shared state:

```text
Flight Agent writes findings into state
Hotel Agent reads those findings
Hotel recommendation becomes arrival-aware
```

Also run:

```bash
python multi_agent/examples/08_handoff_and_state.py
```

This shows the difference between a weak handoff ("please handle this") and a structured handoff with trip context.

---



## 5. Sequential workflow

In a sequential workflow, order is fixed:

```text
Flight Agent
      ↓
Hotel Agent
      ↓
Itinerary Agent
```

This fits travel planning when:

1. choose travel first
2. then stay
3. then build the day plan



### LangGraph building blocks


| Concept    | In this project                               |
| ---------- | --------------------------------------------- |
| State      | `TravelState`                                 |
| Node       | `flight_node`, `hotel_node`, `itinerary_node` |
| Edge       | flight → hotel → itinerary                    |
| Boundaries | START → ... → END                             |


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

A node is a function:

```text
input: state
output: partial state update
```

Example:

```python
return {"flights": findings}
```



### Run sequential

```bash
python -m multi_agent.main sequential
python multi_agent/examples/04_sequential_demo.py
```

Custom query:

```bash
python -m multi_agent.main sequential --query "Plan Hyderabad to Delhi on 2026-04-15 with airport hotel and itinerary"
```



### Live demo queries

**Full trip**

```text
Plan a trip from Hyderabad to Delhi on 2026-04-15: find a flight, a hotel near the airport, and prepare a 3-day itinerary.
```

**Business trip**

```text
Plan a business trip from Hyderabad to Delhi with airport hotel and meeting-friendly timings.
```

**Budget trip**

```text
Plan a budget 3-day Delhi trip from Hyderabad focusing on low hotel cost.
```

**Family trip**

```text
Plan Hyderabad to Jaipur for a family of 3, prefer afternoon flight and a central hotel, then give a sightseeing itinerary.
```

**Weekend leisure**

```text
Plan Bangalore to Goa for a weekend: evening flight, beach hotel, and a relaxed 2-day itinerary.
```



### What to inspect after each run

```text
Input
 ↓
Flight output
 ↓
Hotel output
 ↓
Itinerary / final answer
```

Check whether:

- hotel city matches flight destination
- hotel preference matches arrival time
- itinerary uses both previous outputs



### Extra sequential scenario walkthrough

Request:

```text
"I arrive Delhi at night from Hyderabad and need a hotel plus 2-day plan."
```

Expected flow:

```text
Flight Agent
  → identifies night arrival risk / evening options

Hotel Agent
  → prioritizes airport / late check-in convenience

Itinerary Agent
  → Day 1 becomes arrival + rest, not heavy sightseeing
```

---



## 6. Observability and failure modes

If LangSmith is configured, open the project and inspect the trace:

```text
Workflow
│
├── Flight Agent
│     ├── Input
│     ├── LLM / tool calls
│     └── Output
│
├── Hotel Agent
│     ├── Input (includes flight findings)
│     ├── LLM / tool calls
│     └── Output
│
└── Itinerary Agent
      ├── Input (flights + hotels)
      ├── LLM call
      └── Output
```



### Failure mode examples

**1. Bad flight parsing**

```text
User: "Plan HYD to DEL"
Flight Agent wrongly assumes destination = Hyderabad
  → Hotel Agent searches Hyderabad hotels
  → Final itinerary collapses
```

**2. Context overload**

```text
Flight Agent dumps very large JSON
  → Hotel prompt becomes noisy
  → model misses "near airport"
  → token cost rises
```

**3. Responsibility overlap**

```text
Flight Agent also recommends hotels
Hotel Agent becomes unclear
Debugging becomes harder
```

**4. Missing fields**

```text
No travel date in request
  → flight lookup weak
  → itinerary filled with assumptions
```

**5. Conflicting recommendations**

```text
Flight suggests late arrival
Hotel suggests far city-center stay with early checkout
Itinerary must reconcile or call out conflict
```

Practical habit: each agent should have a clear contract.

```text
Expected input
Expected output
Forbidden responsibilities
```

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

### Example C — itinerary review only

```text
"Review this itinerary for missing information."
```

Maybe only itinerary/review work is needed.

### Example D — already has flight, needs hotel + plan

```text
"I already booked HYD-DEL morning flight. Find airport hotel and make itinerary."
```

Fixed pipeline still forces a fresh flight stage.

### Router vs Supervisor

Run:

```bash
python multi_agent/examples/06_router_vs_supervisor.py
```


| Pattern    | Behavior                                |
| ---------- | --------------------------------------- |
| Router     | Choose one specialist, often stop       |
| Supervisor | Choose next worker, repeat until FINISH |


```text
Router:
"Which one agent should handle this?"

Supervisor:
"Which agent should work next, and are we done yet?"
```

---



## 8. Supervisor workflow

Supervisor architecture:

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
"I need an agent to decide the order."
```



### Run supervisor

```bash
python -m multi_agent.main supervisor
python multi_agent/examples/05_supervisor_demo.py
python multi_agent/examples/09_supervisor_routing_cases.py
```

Custom:

```bash
python -m multi_agent.main supervisor --query "Only research flights from Hyderabad to Delhi on 2026-04-15."
```



### Routing examples to present

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

**Case 4 — itinerary from existing context**

```text
I already have flight and hotel findings. Build the final itinerary only.
```

Expected path:

```text
supervisor → itinerary → FINISH
```

(If findings are empty in state, supervisor may first gather missing pieces.)

**Case 5 — vague request**

```text
Help me plan Delhi travel.
```

Possible path:

```text
supervisor → flight → hotel → itinerary → FINISH
```

Supervisor treats this as a full planning request.

**Case 6 — constrained request**

```text
Find only morning flights HYD to DEL. Do not plan hotel.
```

Expected path:

```text
supervisor → flight → FINISH
```



### Safety

Supervisor loops can go forever without limits. This project uses:

```text
MAX_STEPS = 6
```

After the limit, force `FINISH`.

---



## 9. Sequential vs Supervisor


| Sequential Workflow            | Supervisor Workflow              |
| ------------------------------ | -------------------------------- |
| Fixed execution order          | Dynamic execution                |
| A → B → C                      | Supervisor → Agent → Supervisor  |
| Simple                         | More flexible                    |
| Predictable                    | Decision-based                   |
| Good for pipelines             | Good for mixed intents           |
| Lower orchestration complexity | Higher orchestration complexity  |
| Every step usually runs        | Only needed steps may run        |
| Best for fixed travel packages | Best for varying travel requests |




### Same request, two interpretations

Request:

```text
"Research GenAI" became "Research flights" in travel domain.
```

Travel equivalents:

```text
Sequential always runs full package planning.
Supervisor can stop after flight research.
```

---



## 10. Parallel concept (preview)

From orchestration theory, independent travel tasks can also run in parallel:

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

Run the concept demo:

```bash
python multi_agent/examples/10_parallel_travel_concept.py
```

Use this to contrast:

```text
Sequential: hotel waits for flight
Parallel: flight and hotel can start together when independent
Supervisor: decides what is needed based on the request
```

---



## 11. More presentation examples by theme



### Theme A — City pairs

```text
Hyderabad → Delhi
Bangalore → Goa
Chennai → Hyderabad
Mumbai → Jaipur
Pune → Bangalore
```



### Theme B — Intent types

```text
Flight-only research
Hotel-only search
Full trip package
Itinerary review
Budget optimization
Business meeting trip
Family sightseeing trip
```



### Theme C — Constraint language

```text
"near airport"
"under ₹5000"
"morning flight only"
"late check-in"
"2 days only"
"no hotel needed"
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

4) "Review the previous itinerary for missing information."
   → itinerary → FINISH
```

Then run and compare against `steps` in the supervisor output.

---



## 12. Extension ideas



### Extension 1 — Writer / Booking Agent in sequential

```text
Flight → Hotel → Itinerary → Booking/Writer
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



### Extension 3 — Dynamic routing challenge

Give these three prompts and compare routes:

```text
"Research flights Hyderabad to Delhi."
"Analyze these hotel options and pick one near airport."
"Review this answer for missing information."
```

---



## 13. End-to-end picture

```text
                    MULTI-AGENT TRAVEL SYSTEM
                              |
               ┌──────────────┴──────────────┐
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



### Concepts covered

```text
Python
 → LangChain
 → LangGraph
 → Specialized Agents
 → Shared State
 → Nodes and Edges
 → Conditional Routing
 → Sequential Workflow
 → Supervisor Workflow
 → LangSmith Observability
```



### Key takeaway

```text
Sequential: "I already know the order."
Supervisor: "I need an agent to decide the order."
```

This makes the next topics easier: conditional workflows, parallel workflows, human-in-the-loop, hierarchical orchestration, and MCP-based agent systems.

---



## 14. Command cheat sheet

```bash
cd travel_agent

# concept demos
python multi_agent/examples/01_single_agent_baseline.py
python multi_agent/examples/03_shared_state_demo.py
python multi_agent/examples/06_router_vs_supervisor.py
python multi_agent/examples/07_bad_vs_good_boundaries.py
python multi_agent/examples/08_handoff_and_state.py
python multi_agent/examples/10_parallel_travel_concept.py

# specialists
python multi_agent/examples/02_unit_test_each_agent.py
python -m multi_agent.agents.flight_agent
python -m multi_agent.agents.hotel_agent
python -m multi_agent.agents.itinerary_agent

# orchestration
python -m multi_agent.main sequential
python -m multi_agent.main supervisor
python -m multi_agent.main both
python multi_agent/examples/04_sequential_demo.py
python multi_agent/examples/05_supervisor_demo.py
python multi_agent/examples/09_supervisor_routing_cases.py
```



### If Gemini key is missing

Use concept demos that do not need the model:

```bash
python multi_agent/examples/03_shared_state_demo.py
python multi_agent/examples/06_router_vs_supervisor.py
python multi_agent/examples/07_bad_vs_good_boundaries.py
python multi_agent/examples/08_handoff_and_state.py
python multi_agent/examples/10_parallel_travel_concept.py
```



### If Postgres is down

Continue with orchestration demos. Flight/Hotel agents can still produce structured LLM findings and report that DB lookup failed. This is useful to explain:

```text
Data plane can fail
Orchestration plane can still run
```

---



## 15. Project file map

```text
travel_agent/multi_agent/
├── MULTI_AGENT_TRAVEL_PRESENTATION.md
├── llm.py
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

