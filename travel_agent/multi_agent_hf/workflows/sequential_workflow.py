"""
Sequential multi-agent travel workflow.

START → Flight Agent → Hotel Agent → Itinerary Agent → END
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from multi_agent_hf.agents.flight_agent import run_flight_agent
from multi_agent_hf.agents.hotel_agent import run_hotel_agent
from multi_agent_hf.agents.itinerary_agent import run_itinerary_agent
from multi_agent_hf.workflows.state import TravelState


def flight_node(state: TravelState) -> dict:
    findings = run_flight_agent(state["request"])
    return {"flights": findings}


def hotel_node(state: TravelState) -> dict:
    findings = run_hotel_agent(
        request=state["request"],
        flight_findings=state.get("flights", ""),
    )
    return {"hotels": findings}


def itinerary_node(state: TravelState) -> dict:
    plan = run_itinerary_agent(
        request=state["request"],
        flight_findings=state.get("flights", ""),
        hotel_findings=state.get("hotels", ""),
    )
    return {"itinerary": plan, "final_answer": plan}


def build_sequential_workflow():
    """Compile the fixed Flight → Hotel → Itinerary graph."""
    graph = StateGraph(TravelState)
    graph.add_node("flight", flight_node)
    graph.add_node("hotel", hotel_node)
    graph.add_node("itinerary", itinerary_node)

    graph.add_edge(START, "flight")
    graph.add_edge("flight", "hotel")
    graph.add_edge("hotel", "itinerary")
    graph.add_edge("itinerary", END)

    return graph.compile()


def run_sequential(request: str) -> TravelState:
    """Execute the sequential travel workflow for one user request."""
    app = build_sequential_workflow()
    result = app.invoke(
        {
            "request": request,
            "flights": "",
            "hotels": "",
            "itinerary": "",
            "final_answer": "",
        }
    )
    return result


if __name__ == "__main__":
    query = (
        "Book me a conceptual plan: flight from Hyderabad to Delhi on "
        "2026-04-15, hotel near the airport, and a 3-day itinerary."
    )
    print("=== Sequential Workflow ===\n")
    output = run_sequential(query)
    print("--- FLIGHTS ---\n", output.get("flights", ""), "\n")
    print("--- HOTELS ---\n", output.get("hotels", ""), "\n")
    print("--- FINAL ITINERARY ---\n", output.get("final_answer", ""))
