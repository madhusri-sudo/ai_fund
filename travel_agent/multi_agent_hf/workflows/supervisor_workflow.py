"""
Supervisor multi-agent travel workflow.

Routing is rule-based (reliable for local HF).
Workers gather inventory; a dedicated final_answer node always calls the LLM.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from multi_agent_hf.agents.final_answer import generate_final_answer
from multi_agent_hf.agents.flight_agent import run_flight_agent
from multi_agent_hf.agents.hotel_agent import run_hotel_agent
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
    final_answer = bool(state.get("final_answer"))

    # After workers are done, always go to LLM final answer once.
    if final_answer:
        return "FINISH"

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
        if need_flight and not flights:
            return "flight"
        if need_hotel and not hotels:
            return "hotel"
        return "itinerary"

    # Inventory gathered (or not needed) → LLM final answer
    return "final_answer"


def supervisor_node(state: SupervisorState) -> dict:
    """Decide which worker / final LLM step should run next."""
    steps = list(state.get("steps") or [])
    if len(steps) >= MAX_STEPS:
        # Force LLM final answer if missing, else finish
        if not state.get("final_answer"):
            next_agent = "final_answer"
        else:
            next_agent = "FINISH"
        steps.append(f"supervisor:{next_agent}(max)")
        return {"next_agent": next_agent, "steps": steps}

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
    """
    Mark itinerary stage complete.

    The natural-language answer is produced by final_answer_node (LLM).
    """
    steps = list(state.get("steps") or []) + ["worker:itinerary"]
    return {"itinerary": "ready", "steps": steps}


def final_answer_node(state: SupervisorState) -> dict:
    """Always call the LLM to write the user-facing final answer."""
    answer = generate_final_answer(
        request=state.get("request", ""),
        flight_findings=state.get("flights", ""),
        hotel_findings=state.get("hotels", ""),
    )
    steps = list(state.get("steps") or []) + ["llm:final_answer"]
    return {"final_answer": answer, "steps": steps}


def route_from_supervisor(state: SupervisorState) -> str:
    nxt = state.get("next_agent", "FINISH")
    if nxt in {"flight", "hotel", "itinerary", "final_answer"}:
        return nxt
    return "FINISH"


def build_supervisor_workflow():
    """
    Compile supervisor graph:

    START → supervisor ⇄ (flight|hotel|itinerary)
                      → final_answer (LLM) → supervisor → FINISH → END
    """
    graph = StateGraph(SupervisorState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("flight", flight_node)
    graph.add_node("hotel", hotel_node)
    graph.add_node("itinerary", itinerary_node)
    graph.add_node("final_answer", final_answer_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "flight": "flight",
            "hotel": "hotel",
            "itinerary": "itinerary",
            "final_answer": "final_answer",
            "FINISH": END,
        },
    )

    # Workers and LLM final answer report back to supervisor
    graph.add_edge("flight", "supervisor")
    graph.add_edge("hotel", "supervisor")
    graph.add_edge("itinerary", "supervisor")
    graph.add_edge("final_answer", "supervisor")

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
    print("\n--- FINAL (LLM) ---\n")
    print(output.get("final_answer", ""))
