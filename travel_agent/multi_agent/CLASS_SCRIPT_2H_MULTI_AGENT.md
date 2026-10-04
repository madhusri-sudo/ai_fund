# Practical

## Multi-Agent Orchestration with Travel Agent

### Focus: Sequential Workflow + Supervisor Workflow

> **Project:** Multi-Agent Travel Planner inside `travel_agent/`  
> **Stack:** Python · LangChain · LangGraph · Google Gemini · LangSmith · python-dotenv · existing Postgres inventory

---

## How to use this script

- Text under **SAY** is what you speak.
- Text under **DO** is what you type/run on screen.
- Text under **ASK** is a short classroom question.
- Timings are guides. Keep theory short; keep coding long.

**Before class checklist**

1. `cd travel_agent`
2. `.env` has `GOOGLE_API_KEY` / `GEMINI_API_KEY`
3. Optional but recommended: Postgres seeded (`python scripts/init_db.py` + `python scripts/seed_demo_data.py`)
4. `pip install -r requirements.txt` (includes `langgraph`)
5. LangSmith keys optional but great for Part 7

---



# Opening (0:00 – 0:10)



## Part 1 — Project Introduction



### SAY

```text
In the previous session we covered Multi-Agent Orchestration theory.

Today is 100% practical.

We will not jump between random demos.
We will build ONE project progressively:

Single Agent
    → Specialized Agents
    → Sequential Workflow
    → Supervisor Workflow

The project is a Multi-Agent Travel Planner.

User request example:
"Book me a flight from Hyderabad to Delhi,
find a hotel near the airport,
and prepare my itinerary."

Instead of one agent doing everything, we will create specialists.
```



### DO

Draw on board / show slide:

```text
                    USER QUERY
                        |
                        v
              ┌───────────────────┐
              │   Flight Agent    │
              └─────────┬─────────┘
                        |
                        v
              ┌───────────────────┐
              │   Hotel Agent     │
              └─────────┬─────────┘
                        |
                        v
              ┌───────────────────┐
              │ Itinerary Agent   │
              └─────────┬─────────┘
                        |
                        v
                  FINAL PLAN
```

Then show the supervisor target:

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



### SAY

```text
Quick vocabulary refresh only — no long theory.

Agent:
Performs one responsibility.

Workflow:
Defines how agents are connected.

Supervisor:
An orchestrator agent that decides which worker runs next.

Worker agent:
A specialist that does the actual work.

Shared state:
The common workspace where intermediate results are stored.
```



### ASK

```text
Why not put flight search, hotel search, and itinerary writing
inside one giant agent prompt?
```



### Expected student answers / your wrap-up

```text
- Harder to control quality
- Harder to debug
- Tools get mixed
- Responsibilities overlap
- One failure pollutes the whole answer
```



### SAY

```text
Our three agents:

1) Flight Agent
Input: travel request
Output: flight findings

2) Hotel Agent
Input: travel request + optional flight findings
Output: hotel findings

3) Itinerary Agent
Input: request + flights + hotels
Output: reviewed final plan

Clear boundaries are the foundation of multi-agent design.
```

---



# Part 2 — Project Setup (0:10 – 0:20)



### SAY

```text
We already have a working single-agent travel project under travel_agent/.

Today we add a multi_agent package beside it.

This is intentional:
First you understand one agent with tools.
Then you learn orchestration of many agents.
```



### DO

Show folder structure:

```text
travel_agent/
├── app/                         # existing single-agent system
├── multi_agent/
│   ├── llm.py
│   ├── main.py
│   ├── agents/
│   │   ├── flight_agent.py
│   │   ├── hotel_agent.py
│   │   └── itinerary_agent.py
│   ├── workflows/
│   │   ├── state.py
│   │   ├── sequential_workflow.py
│   │   └── supervisor_workflow.py
│   ├── examples/
│   │   ├── 01_single_agent_baseline.py
│   │   ├── 02_unit_test_each_agent.py
│   │   ├── 03_shared_state_demo.py
│   │   ├── 04_sequential_demo.py
│   │   ├── 05_supervisor_demo.py
│   │   └── 06_router_vs_supervisor.py
│   └── CLASS_SCRIPT_2H_MULTI_AGENT.md
```



### DO

Open `.env` / `.env.example` and mention:

```env
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-3.8-flash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=travel-agent
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/travel_agent
```



### SAY

```text
Why LangSmith matters today:

Without tracing, a multi-agent app looks like a black box.

With tracing you can see:
User
 → Supervisor
 → Flight Agent
 → Hotel Agent
 → Itinerary Agent
 → Final answer

You will debug orchestration, not guess.
```



### DO

Run baseline single-agent example:

```bash
cd travel_agent
python multi_agent/examples/01_single_agent_baseline.py
```



### SAY

```text
This baseline is useful.
But notice the problem: one response tries to do everything.

Soon we will force specialization.
```

---



# Part 3 — Create / Test Individual Agents (0:20 – 0:40)



### SAY

```text
Important practical rule:

First make every agent work independently.
Then connect them.

Development order:
Agent Development
    → Unit Testing
    → Orchestration
```



## 3A. Flight Agent



### DO

Open `multi_agent/agents/flight_agent.py`.

Highlight:

- system prompt boundaries (“ONLY flights”)
- optional DB lookup through existing `flight_service`
- `run_flight_agent()`



### SAY

```text
The Flight Agent is not a travel manager.
It is a specialist.

Good prompt design means saying what NOT to do:
Do not plan hotels.
Do not create final itinerary.
```



### DO

```bash
python -m multi_agent.agents.flight_agent
```

or

```bash
python multi_agent/examples/02_unit_test_each_agent.py
```



### SAY

```text
Expected style of output:
- route
- date
- candidate flights
- recommendation notes

If DB is seeded, real inventory appears.
If DB is down, the agent still produces structured flight reasoning,
and we discuss fallback behavior.
```



## 3B. Hotel Agent



### DO

Open `multi_agent/agents/hotel_agent.py`.

### SAY

```text
Hotel Agent receives prior flight findings when available.

Why?
Because arrival city and timing affect hotel choice.
This is shared-context thinking, even before full LangGraph state.
```



### ASK

```text
If Flight Agent already recommended Delhi arrival at 9 PM,
what should Hotel Agent optimize for?
```



### Wrap-up

```text
Late check-in friendliness / airport proximity / transport ease.
Specialization still uses context.
```



## 3C. Itinerary Agent



### DO

Open `multi_agent/agents/itinerary_agent.py`.

### SAY

```text
Itinerary Agent is our review + synthesis stage.

It checks:
- completeness
- contradictions
- missing info
- unsupported claims
- practical day-by-day structure

In the research-assistant version this was called Review Agent.
In travel, synthesis naturally becomes itinerary creation.
```



### DO

Finish running `02_unit_test_each_agent.py` and inspect all three outputs.

### SAY

```text
At this point we have three working specialists.
We do NOT have orchestration yet.

That is good.
We earned the right to connect them.
```

---



# Part 4 — Shared State + Sequential Workflow (0:40 – 1:05)



## 4A. Shared State concept



### DO

```bash
python multi_agent/examples/03_shared_state_demo.py
```



### SAY

```text
Shared state is the shared workspace.

Initial:
request = user text
flights = empty
hotels = empty
itinerary = empty
final_answer = empty

After Flight Agent:
flights = filled

After Hotel Agent:
hotels = filled

After Itinerary Agent:
itinerary + final_answer = filled

Agents collaborate through state updates.
They do not need to re-ask the user for everything.
```



### DO

Open `multi_agent/workflows/state.py` and show `TravelState`.

## 4B. What is Sequential Workflow?



### SAY

```text
Sequential means fixed order:

Flight
  → Hotel
  → Itinerary

Output of one becomes input context for the next.

This matches travel planning when:
you usually pick destination travel first,
then stay,
then build the day plan.
```



### DO

Open `multi_agent/workflows/sequential_workflow.py`.

Walk through:

1. `flight_node`
2. `hotel_node`
3. `itinerary_node`
4. edges: START → flight → hotel → itinerary → END



### SAY

```text
Four LangGraph ideas:

State = shared data
Node = unit of work
Edge = execution path
START/END = workflow boundaries
```



### DO

Build/compile mentally with students:

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

---



# Part 5 — LangGraph Nodes Deep Dive (1:05 – 1:20)



### SAY

```text
A node is just a function:

input: state
output: partial state update

Example:
flight_node reads state["request"]
writes state["flights"]

LangGraph merges the update into shared state.
```



### DO

Point to return dictionaries:

```python
return {"flights": findings}
```



### SAY

```text
This is cleaner than passing giant prompt strings manually
between scripts.

The graph owns the flow.
The nodes own the work.
The state owns the memory of the run.
```



### ASK

```text
If Hotel Agent fails, what happens to Itinerary Agent
in a pure sequential workflow?
```



### Wrap-up

```text
It still runs, but with weak/empty hotel context.
That is both a strength and a weakness of fixed pipelines.
Later, supervisor/validation can decide to retry or stop.
```

---



# Part 6 — Run Sequential Workflow (1:20 – 1:30)



### DO

```bash
python -m multi_agent.main sequential
```

Also run:

```bash
python multi_agent/examples/04_sequential_demo.py
```



### Test queries to demo

**Test 1**

```text
What flights and hotels work for Hyderabad to Delhi on 2026-04-15,
and what should a 3-day itinerary look like?
```

**Test 2**

```text
Plan a business trip from Hyderabad to Delhi with airport hotel.
```

**Test 3**

```text
Plan a budget 3-day Delhi trip from Hyderabad focusing on low hotel cost.
```



### SAY

```text
For each run, inspect the chain:

Input
 ↓
Flight output
 ↓
Hotel output
 ↓
Itinerary / final answer

Ask students to notice whether hotel recommendations
actually use flight destination context.
```



### DO

Optional custom query:

```bash
python -m multi_agent.main sequential --query "Plan Hyderabad to Delhi on 2026-04-15 with airport hotel and itinerary"
```

---



# Part 7 — Debugging & LangSmith (1:30 – 1:40)



### SAY

```text
Now we debug like engineers, not magicians.
```



### DO

Open LangSmith project (`travel-agent` or your configured project).
Show one sequential trace.

### SAY

```text
Ideal trace shape:

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



### Failure modes to discuss (with travel examples)

**Problem 1 — Bad flight research**

```text
Wrong destination parsed
  → hotel in wrong city
  → itinerary nonsense
```

**Problem 2 — Too much context**

```text
Flight agent dumps huge JSON
  → hotel prompt becomes noisy
  → token cost rises
  → model misses key constraints
```

**Problem 3 — Responsibility overlap**

```text
If Flight Agent also recommends hotels,
Hotel Agent becomes unclear.
Keep boundaries sharp.
```



### SAY

```text
Production habit:
Log each agent’s contract:
expected input, expected output, forbidden responsibilities.
```

---



# Part 8 — Why Sequential Is Not Always Enough (1:40 – 1:45)



### SAY

```text
Sequential is excellent for fixed pipelines.

But every request currently does:

Flight → Hotel → Itinerary

What if user says:
"Only research flights from Hyderabad to Delhi."

Do we still need hotel and itinerary?

What if user says:
"Review this itinerary for missing information."

Maybe only itinerary/review is needed.

Fixed workflows cannot dynamically ask:
Which agent should work next?
```



### DO

```bash
python multi_agent/examples/06_router_vs_supervisor.py
```



### SAY

```text
Quick distinction:

Router:
Choose one specialist and often stop.

Supervisor:
Decide next worker, collect result, decide again, until FINISH.

Today’s second architecture is Supervisor.
```

---



# Part 9 — Supervisor Workflow (1:45 – 2:00)



### SAY

```text
Supervisor architecture:

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



### DO

Open `multi_agent/workflows/supervisor_workflow.py`.

Cover:

- `SupervisorState` with `next_agent`
- `supervisor_node` decision prompt
- conditional edges
- workers return to supervisor
- `MAX_STEPS` safety stop



### SAY

```text
Supervisor decides one of:
flight
hotel
itinerary
FINISH

This is the key line in the mental model:

Sequential:
"I already know the order."

Supervisor:
"I need an agent to decide the order."
```



### DO

```bash
python -m multi_agent.main supervisor --query "Only research flights from Hyderabad to Delhi on 2026-04-15."
```

Then:

```bash
python multi_agent/examples/05_supervisor_demo.py
```



### SAY

```text
Observe routing steps.

For flight-only request, good supervisor behavior:
supervisor → flight → supervisor → FINISH

For full trip request:
supervisor → flight → hotel → itinerary → FINISH
(order may vary slightly, but should be purposeful)
```



### Comparison table (say it out loud)


| Sequential                     | Supervisor                      |
| ------------------------------ | ------------------------------- |
| Fixed order                    | Dynamic order                   |
| A → B → C                      | Supervisor → Agent → Supervisor |
| Simple                         | More flexible                   |
| Predictable                    | Decision-based                  |
| Great for pipelines            | Great for collaboration         |
| Lower orchestration complexity | Higher orchestration complexity |
| Every step usually runs        | Only needed steps run           |
| Best for fixed travel packages | Best for mixed travel intents   |


---



# Closing Exercises (use remaining minutes)



## Exercise 1 — Add Booking Agent (sequential)

```text
Current:
Flight → Hotel → Itinerary

Add:
Booking Agent

New:
Flight → Hotel → Itinerary → Booking
```

**SAY**

```text
Booking Agent should only create bookings from approved itinerary choices.
It should not re-search inventory from scratch.
```



## Exercise 2 — Add Fact / Policy Checker (supervisor)

```text
Supervisor workers:
- flight
- hotel
- policy_checker
- itinerary
```

**SAY**

```text
Policy checker can validate:
- passport/id reminders
- cancellation windows
- budget constraints
Supervisor decides when policy checking is necessary.
```



## Exercise 3 — Dynamic routing challenge

Give three prompts and predict routes before running:

```text
1) "Research flights Hyderabad to Delhi."
2) "Analyze these hotel options and pick one near airport."
3) "Review the itinerary for missing information."
```

Then run supervisor and compare predictions vs actual `steps`.

---



# Final board summary (last 2 minutes)



### SAY

```text
What we built today:

                    MULTI-AGENT TRAVEL PRACTICAL
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



### SAY

```text
Technologies touched:
Python → LangChain → LangGraph → Shared State → Nodes → Edges
→ Conditional Routing → Sequential → Supervisor → LangSmith

Key outcome:
Not merely "three agents exist",
but understanding the architectural difference:

Sequential: known order
Supervisor: decided order

This prepares the next topics:
parallel workflows, human-in-the-loop, hierarchical orchestration, MCP tool networks.
```

---



# Instructor runbook (cheat sheet)



## Commands

```bash
cd travel_agent

# tiny concept demos (no/low cost)
python multi_agent/examples/03_shared_state_demo.py
python multi_agent/examples/06_router_vs_supervisor.py

# agent unit tests
python multi_agent/examples/02_unit_test_each_agent.py

# main patterns
python -m multi_agent.main sequential
python -m multi_agent.main supervisor
python -m multi_agent.main both

# focused demos
python multi_agent/examples/04_sequential_demo.py
python multi_agent/examples/05_supervisor_demo.py
```



## If Gemini key missing

```text
Stop and configure .env.
Do not improvise with fake live calls.
Use 03_shared_state_demo.py and 06_router_vs_supervisor.py to continue teaching concepts.
```



## If Postgres is down

```text
Continue class anyway.
Flight/Hotel agents will report lookup failure and still produce LLM structured findings.
Explain: tools/data plane can fail while orchestration plane still works.
```



## Timing rescue plans

- Behind schedule before Part 9: skip custom Test 3 queries; go straight to supervisor demo.
- Ahead of schedule: do Exercise 1 (Booking Agent design on board) without full coding.

---



# Suggested spoken transitions (copy/paste)

1. **Into setup:** “Theory is done. Now we build one travel system in layers.”
2. **Into unit agents:** “Orchestration on broken agents creates elegant failure. Test specialists first.”
3. **Into state:** “Multi-agent systems need a shared workspace. That workspace is state.”
4. **Into sequential:** “When order is known, hard-code the pipeline.”
5. **Into supervisor:** “When order depends on the request, add a decision-making orchestrator.”
6. **Close:** “Remember the distinction: known order versus decided order.”

---



# Mapping from original research script → travel script


| Original research class      | Travel class                  |
| ---------------------------- | ----------------------------- |
| Research Agent               | Flight Agent                  |
| Analysis Agent               | Hotel Agent                   |
| Review Agent                 | Itinerary Agent               |
| Research findings            | Flight findings               |
| Structured analysis          | Hotel recommendation analysis |
| Reviewed final response      | Final itinerary plan          |
| Research question            | Travel request                |
| Sequential research pipeline | Sequential trip pipeline      |
| Supervisor research workers  | Supervisor travel workers     |


Same orchestration lesson. Domain changed to match your Travel Agent project and the PDF travel example.