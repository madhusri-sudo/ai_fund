"""
Supervisor multi-agent travel workflow.

For local HF models, routing is rule-based (TinyLlama is unreliable at
returning only flight/hotel/itinerary/FINISH). Workers still use inventory.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from multi_agent_hf.agents.flight_agent import run_flight_agent
from multi_agent_hf.agents.hotel_agent import run_hotel_agent
from multi_agent_hf.agents.itinerary_agent import run_itinerary_agent
from multi_agent_hf.workflows.state import SupervisorState

MAX_STEPS = 8


def _wants_flight(request: str) -> bool:
    q = request.lower()
    if "only" in q and "hotel" in q and "flight" not in q:
        return False
    if "do not plan hotel" in q or "don't plan hotel" in q:
        return "flight" in q or "hyd" in q or "delhi" in q or "trip" in q
    return any(
        key in q
        for key in (
            "flight",
            "fly",
            "airport to",
            "from ",
            "trip",
            "travel",
            "itinerary",
            "plan",
        )
    )


def _wants_hotel(request: str) -> bool:
    q = request.lower()
    if "do not plan hotel" in q or "don't plan hotel" in q or "no hotel" in q:
        return False
    if "only" in q and "flight" in q and "hotel" not in q:
        return False
    return any(key in q for key in ("hotel", "stay", "room", "trip", "plan", "itinerary"))


def _wants_itinerary(request: str) -> bool:
    q = request.lower()
    if "only" in q and ("flight" in q or "hotel" in q) and "itinerary" not in q:
        return False
    return any(key in q for key in ("itinerary", "plan", "full trip", "day-by-day", "schedule"))


def _decide_next(state: SupervisorState) -> str:
    """Deterministic supervisor policy for local demos."""
    request = state.get("request", "")
    flights = bool(state.get("flights"))
    hotels = bool(state.get("hotels"))
    itinerary = bool(state.get("itinerary"))

    need_flight = _wants_flight(request)
    need_hotel = _wants_hotel(request)
    need_itinerary = _wants_itinerary(request)

    # Pure hotel request
    if "hotel" in request.lower() and "flight" not in request.lower() and not need_itinerary:
        need_flight = False
        need_hotel = True
        need_itinerary = False

    # Pure flight research
    if "only" in request.lower() and "flight" in request.lower():
        need_flight = True
        need_hotel = False
        need_itinerary = False

    if need_flight and not flights:
        return "flight"
    if need_hotel and not hotels:
        return "hotel"
    if need_itinerary and not itinerary:
        # For full plans, require flight/hotel first when those were requested
        if need_flight and not flights:
            return "flight"
        if need_hotel and not hotels:
            return "hotel"
        return "itinerary"

    return "FINISH"


def supervisor_node(state: SupervisorState) -> dict:
    """Decide which worker should run next."""
    steps = list(state.get("steps") or [])
    if len(steps) >= MAX_STEPS:
        return {"next_agent": "FINISH", "steps": steps + ["supervisor:FINISH(max)"]}

    next_agent = _decide_next(state)
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
    print("\n--- FINAL ---\n")
    print(output.get("final_answer") or output.get("flights") or output.get("hotels"))
