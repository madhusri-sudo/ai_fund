"""
Supervisor multi-agent travel workflow.

Supervisor decides dynamically:
  flight | hotel | itinerary | FINISH
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from multi_agent.agents.flight_agent import run_flight_agent
from multi_agent.agents.hotel_agent import run_hotel_agent
from multi_agent.agents.itinerary_agent import run_itinerary_agent
from multi_agent.llm import invoke_text
from multi_agent.workflows.state import SupervisorState

MAX_STEPS = 6

SUPERVISOR_SYSTEM_PROMPT = """
You are the Travel Supervisor (orchestrator).

You coordinate three worker agents:
- flight: searches and summarizes flights
- hotel: searches and summarizes hotels
- itinerary: builds / reviews the final trip plan
- FINISH: workflow is complete

Decision rules:
1. If the user needs flight info and flights are empty → flight
2. If the user needs hotel info and hotels are empty → hotel
3. If both flight and hotel work are done (or not needed) and itinerary is empty → itinerary
4. If the request is only about flights → flight then FINISH (itinerary optional)
5. If the request is only about hotels → hotel then FINISH
6. If the request is only "review/build itinerary" and findings exist → itinerary
7. If final plan is ready → FINISH
8. Never loop forever. Prefer FINISH when enough information exists.

Reply with ONLY one token from this set:
flight
hotel
itinerary
FINISH
"""


def _normalize_next(raw: str) -> str:
    text = raw.strip().upper()
    if "FINISH" in text:
        return "FINISH"
    lowered = raw.strip().lower()
    for option in ("flight", "hotel", "itinerary"):
        if option in lowered:
            return option
    # Fallback: if nothing clear, finish safely
    return "FINISH"


def supervisor_node(state: SupervisorState) -> dict:
    """Decide which worker should run next."""
    steps = list(state.get("steps") or [])
    if len(steps) >= MAX_STEPS:
        return {"next_agent": "FINISH", "steps": steps + ["supervisor:FINISH(max)"]}

    prompt = f"""
User request:
{state.get("request", "")}

Current shared state:
- flights: {"PRESENT" if state.get("flights") else "EMPTY"}
- hotels: {"PRESENT" if state.get("hotels") else "EMPTY"}
- itinerary: {"PRESENT" if state.get("itinerary") else "EMPTY"}

Steps so far: {steps}
"""
    decision_raw = invoke_text(SUPERVISOR_SYSTEM_PROMPT, prompt, temperature=0)
    next_agent = _normalize_next(decision_raw)
    steps.append(f"supervisor:{next_agent}")
    return {"next_agent": next_agent, "steps": steps}


def flight_node(state: SupervisorState) -> dict:
    findings = run_flight_agent(state["request"])
    steps = list(state.get("steps") or []) + ["worker:flight"]
    return {"flights": findings, "steps": steps}


def hotel_node(state: SupervisorState) -> dict:
    findings = run_hotel_agent(
        request=state["request"],
        flight_findings=state.get("flights", ""),
    )
    steps = list(state.get("steps") or []) + ["worker:hotel"]
    return {"hotels": findings, "steps": steps}


def itinerary_node(state: SupervisorState) -> dict:
    plan = run_itinerary_agent(
        request=state["request"],
        flight_findings=state.get("flights", ""),
        hotel_findings=state.get("hotels", ""),
    )
    steps = list(state.get("steps") or []) + ["worker:itinerary"]
    return {
        "itinerary": plan,
        "final_answer": plan,
        "steps": steps,
    }


def route_from_supervisor(state: SupervisorState) -> str:
    nxt = state.get("next_agent", "FINISH")
    if nxt in {"flight", "hotel", "itinerary"}:
        return nxt
    return "FINISH"


def build_supervisor_workflow():
    """Compile supervisor ↔ workers graph with conditional routing."""
    graph = StateGraph(SupervisorState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("flight", flight_node)
    graph.add_node("hotel", hotel_node)
    graph.add_node("itinerary", itinerary_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "flight": "flight",
            "hotel": "hotel",
            "itinerary": "itinerary",
            "FINISH": END,
        },
    )

    # Workers always report back to supervisor
    graph.add_edge("flight", "supervisor")
    graph.add_edge("hotel", "supervisor")
    graph.add_edge("itinerary", "supervisor")

    return graph.compile()


def run_supervisor(request: str) -> SupervisorState:
    """Execute the supervisor travel workflow for one user request."""
    app = build_supervisor_workflow()
    result = app.invoke(
        {
            "request": request,
            "flights": "",
            "hotels": "",
            "itinerary": "",
            "final_answer": "",
            "next_agent": "flight",
            "steps": [],
        }
    )
    return result


if __name__ == "__main__":
    query = "Only research flights from Hyderabad to Delhi on 2026-04-15."
    print("=== Supervisor Workflow ===\n")
    output = run_supervisor(query)
    print("Steps:", output.get("steps"))
    print("\n--- FINAL ---\n", output.get("final_answer") or output.get("flights"))
