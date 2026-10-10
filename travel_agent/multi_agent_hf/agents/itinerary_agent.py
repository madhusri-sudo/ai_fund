"""Itinerary / final-answer agent — LLM writes the response from inventory context."""

from __future__ import annotations

from multi_agent_hf.agents.final_answer import generate_final_answer


def run_itinerary_agent(
    request: str,
    flight_findings: str = "",
    hotel_findings: str = "",
) -> str:
    """
    Produce the final travel answer with an LLM call.

    Flight/Hotel agents supply inventory facts.
    This agent asks the LLM to turn those facts into the user-facing answer.
    """
    return generate_final_answer(
        request=request,
        flight_findings=flight_findings,
        hotel_findings=hotel_findings,
    )


if __name__ == "__main__":
    sample_request = "Plan a 3-day Hyderabad to Delhi business trip on 2026-10-10."
    sample_flights = """
Flight findings (FROM INVENTORY)
Lookup: Hyderabad -> Delhi on 2026-10-10
1. AI202 - Air India, 06:30 -> 08:45, INR 5200.0
2. 6E451 - IndiGo, 09:15 -> 11:20, INR 4500.0
Recommendation (from inventory): 6E451 (IndiGo) at INR 4500.0 departing 09:15.
"""
    sample_hotels = """
Hotel findings (FROM INVENTORY)
Lookup city: Delhi
1. Lotus Inn (4 stars), Aerocity, New Delhi, INR 5600.0/night
Recommendation (from inventory): Lotus Inn - INR 5600.0/night at Aerocity, New Delhi.
"""
    print("=== Itinerary / Final Answer Agent (LLM) ===\n")
    print(
        run_itinerary_agent(
            sample_request,
            flight_findings=sample_flights,
            hotel_findings=sample_hotels,
        )
    )
