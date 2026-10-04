"""Flight specialist agent — finds and summarizes flight options."""

from __future__ import annotations

import json
import re

from multi_agent.llm import get_llm, invoke_text

try:
    from app.services import flight_service
except Exception:  # pragma: no cover - optional during lecture demos
    flight_service = None


FLIGHT_SYSTEM_PROMPT = """
You are a Flight Agent in a multi-agent travel system.

Your ONLY responsibility is flights:
- Identify origin, destination, and travel date from the user request
- Summarize available flight options
- Highlight price, timing, and practical constraints

Do NOT plan hotels.
Do NOT create the final itinerary.
Do NOT book anything unless explicitly asked later.

Return a clear structured summary of flight findings.
"""


def _extract_trip_fields(request: str) -> dict[str, str]:
    """Use the LLM to extract origin/destination/date for DB lookup."""
    raw = invoke_text(
        system_prompt=(
            "Extract travel fields as JSON only with keys: "
            "origin, destination, departure_date. "
            "Use YYYY-MM-DD for date. If unknown, use empty string."
        ),
        user_prompt=request,
        temperature=0,
    )
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        return {"origin": "", "destination": "", "departure_date": ""}
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"origin": "", "destination": "", "departure_date": ""}
    return {
        "origin": str(data.get("origin", "")).strip(),
        "destination": str(data.get("destination", "")).strip(),
        "departure_date": str(data.get("departure_date", "")).strip(),
    }


def _lookup_flights(origin: str, destination: str, departure_date: str) -> str:
    if not flight_service or not origin or not destination or not departure_date:
        return (
            "No database flight lookup available "
            "(missing service or incomplete origin/destination/date)."
        )
    try:
        flights = flight_service.get_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
        )
    except Exception as exc:
        return f"Flight database lookup failed: {exc}"

    if not flights:
        return (
            f"No flights found from {origin} to {destination} "
            f"on {departure_date}."
        )
    return json.dumps(flights, indent=2)


def run_flight_agent(request: str, prior_context: str = "") -> str:
    """
    Run the flight agent independently.

    Args:
        request: User travel request / research question.
        prior_context: Optional shared-state context from earlier agents.
    """
    fields = _extract_trip_fields(request)
    inventory = _lookup_flights(
        fields["origin"],
        fields["destination"],
        fields["departure_date"],
    )

    user_prompt = f"""
User request:
{request}

Extracted fields:
{json.dumps(fields, indent=2)}

Flight inventory (from database if available):
{inventory}

Prior context from other agents (may be empty):
{prior_context or "(none)"}

Produce flight findings only.
"""
    return invoke_text(FLIGHT_SYSTEM_PROMPT, user_prompt)


def run_flight_agent_with_tools(request: str) -> str:
    """
    Optional tool-using variant (for advanced demos).

    Uses LangChain create_agent + get_flights tool.
    """
    from langchain.agents import create_agent

    from app.tools.flight_tools import get_flights

    agent = create_agent(
        model=get_llm(temperature=0),
        tools=[get_flights],
        system_prompt=FLIGHT_SYSTEM_PROMPT,
    )
    result = agent.invoke({"messages": [{"role": "user", "content": request}]})
    return str(result["messages"][-1].content)


if __name__ == "__main__":
    sample = (
        "Find flights from Hyderabad to Delhi on 2026-04-15 "
        "for a 3-day business trip."
    )
    print("=== Flight Agent (independent test) ===\n")
    print(run_flight_agent(sample))
