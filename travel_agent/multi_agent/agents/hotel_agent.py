"""Hotel specialist agent — finds and summarizes hotel options."""

from __future__ import annotations

import json
import re

from multi_agent.llm import get_llm, invoke_text

try:
    from app.services import hotel_service
except Exception:  # pragma: no cover
    hotel_service = None


HOTEL_SYSTEM_PROMPT = """
You are a Hotel Agent in a multi-agent travel system.

Your ONLY responsibility is hotels:
- Identify the destination city and stay needs
- Summarize suitable hotel options
- Consider location preference (near airport / city center) when mentioned
- Mention price, stars, and availability when known

Do NOT search flights.
Do NOT create the final day-by-day itinerary.

Return a clear structured summary of hotel findings.
"""


def _extract_city(request: str, flight_findings: str = "") -> str:
    raw = invoke_text(
        system_prompt=(
            "Extract the hotel city as JSON only: {\"city\": \"...\"}. "
            "Prefer destination city from the trip. Empty string if unknown."
        ),
        user_prompt=(
            f"User request:\n{request}\n\n"
            f"Flight findings (may help):\n{flight_findings or '(none)'}"
        ),
        temperature=0,
    )
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        return ""
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return ""
    return str(data.get("city", "")).strip()


def _lookup_hotels(city: str) -> str:
    if not hotel_service or not city:
        return "No database hotel lookup available (missing service or city)."
    try:
        hotels = hotel_service.get_hotels(city=city)
    except Exception as exc:
        return f"Hotel database lookup failed: {exc}"

    if not hotels:
        return f"No hotels found in {city}."
    return json.dumps(hotels, indent=2)


def run_hotel_agent(request: str, flight_findings: str = "") -> str:
    """Run the hotel agent independently (or after flight findings)."""
    city = _extract_city(request, flight_findings)
    inventory = _lookup_hotels(city)

    user_prompt = f"""
User request:
{request}

Detected city: {city or "(unknown)"}

Hotel inventory (from database if available):
{inventory}

Flight findings from previous agent (may be empty):
{flight_findings or "(none)"}

Produce hotel findings only. Prefer hotels that fit flight arrival/location if given.
"""
    return invoke_text(HOTEL_SYSTEM_PROMPT, user_prompt)


def run_hotel_agent_with_tools(request: str) -> str:
    """Optional tool-using variant for advanced demos."""
    from langchain.agents import create_agent

    from app.tools.hotel_tools import get_hotels

    agent = create_agent(
        model=get_llm(temperature=0),
        tools=[get_hotels],
        system_prompt=HOTEL_SYSTEM_PROMPT,
    )
    result = agent.invoke({"messages": [{"role": "user", "content": request}]})
    return str(result["messages"][-1].content)


if __name__ == "__main__":
    sample = (
        "I need a hotel near the airport in Delhi for a 3-day business trip "
        "starting 2026-04-15."
    )
    print("=== Hotel Agent (independent test) ===\n")
    print(run_hotel_agent(sample))
