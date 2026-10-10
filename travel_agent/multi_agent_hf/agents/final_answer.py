"""LLM-written final answer grounded in inventory findings."""

from __future__ import annotations

from multi_agent_hf.llm import invoke_text

FINAL_SYSTEM_PROMPT = """
You are the Final Answer Agent for a multi-agent travel system.

Write a clear, natural-language travel answer for the user.

Rules:
1. Use ONLY the inventory findings provided below.
2. Do NOT invent flight numbers, airlines, hotel names, prices, seats, or dates.
3. If inventory findings are present, recommend from those options.
4. If a section is empty, skip it or say it was not requested / not found.
5. Structure the answer with short sections:
   - Trip summary
   - Flight recommendation (if any)
   - Hotel recommendation (if any)
   - Day-by-day plan (if trip/itinerary was requested)
   - Notes / assumptions
6. Keep the tone helpful and concise.
"""


def _trim_inventory_blob(text: str, max_chars: int = 2500) -> str:
    """Prefer readable inventory lines; drop huge raw JSON tails for the LLM."""
    if not text:
        return "(none)"
    cut = text.find("Raw inventory JSON:")
    if cut == -1:
        cut = text.find("Raw DB JSON:")
    cleaned = text[:cut].strip() if cut != -1 else text.strip()
    if len(cleaned) > max_chars:
        return cleaned[:max_chars] + "\n...(truncated)"
    return cleaned or "(none)"


def generate_final_answer(
    request: str,
    flight_findings: str = "",
    hotel_findings: str = "",
) -> str:
    """
    Always call the LLM to produce the user-facing final answer.

    Inventory text is context only — the model writes the response.
    """
    user_prompt = f"""
User request:
{request}

Flight inventory findings (source of truth):
{_trim_inventory_blob(flight_findings)}

Hotel inventory findings (source of truth):
{_trim_inventory_blob(hotel_findings)}

Write the final answer now. Use only the facts above.
"""
    answer = invoke_text(FINAL_SYSTEM_PROMPT, user_prompt, temperature=0.3)
    return answer.strip()
