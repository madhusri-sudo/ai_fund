"""Itinerary agent — reviews flight + hotel findings and builds final plan."""

from __future__ import annotations

from multi_agent.llm import invoke_text


ITINERARY_SYSTEM_PROMPT = """
You are an Itinerary Agent in a multi-agent travel system.

Your responsibility is to combine flight and hotel findings into a practical trip plan.

Check for:
- Completeness (flight + stay coverage)
- Timing conflicts (late arrival vs hotel check-in assumptions)
- Missing information
- Unsupported claims
- Clear day-by-day structure

Produce a polished final travel plan for the user.
Include:
1. Trip overview
2. Recommended flight choice
3. Recommended hotel choice
4. Day-by-day outline
5. Open questions / assumptions
"""


def run_itinerary_agent(
    request: str,
    flight_findings: str = "",
    hotel_findings: str = "",
) -> str:
    """Build / review the final itinerary from prior agent outputs."""
    user_prompt = f"""
User request:
{request}

Flight findings:
{flight_findings or "(none provided)"}

Hotel findings:
{hotel_findings or "(none provided)"}

Create the reviewed final itinerary.
If critical info is missing, state assumptions clearly.
"""
    return invoke_text(ITINERARY_SYSTEM_PROMPT, user_prompt)


if __name__ == "__main__":
    sample_request = "Plan a 3-day Hyderabad to Delhi business trip."
    sample_flights = (
        "Options: HYD-DEL morning flight ~₹4500; evening flight ~₹5200."
    )
    sample_hotels = (
        "Airport hotel 4-star ~₹3500/night; city center 3-star ~₹2800/night."
    )
    print("=== Itinerary Agent (independent test) ===\n")
    print(
        run_itinerary_agent(
            sample_request,
            flight_findings=sample_flights,
            hotel_findings=sample_hotels,
        )
    )
