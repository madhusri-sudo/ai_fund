import os

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from app.agent.prompts import TRAVEL_AGENT_SYSTEM_PROMPT
from app.config.settings import get_settings
from app.tools.booking_tools import book_flight, book_hotel, cancel_booking
from app.tools.flight_tools import get_flights
from app.tools.hotel_tools import get_hotels


def build_travel_agent():
    """Create the LangChain travel agent with Gemini + tools."""
    settings = get_settings()

    api_key = settings.resolved_google_api_key or os.getenv("GOOGLE_API_KEY", "")

    # Ensure LangSmith / Gemini env vars are visible to SDKs.
    if api_key:
        os.environ.setdefault("GOOGLE_API_KEY", api_key)
    if settings.langchain_api_key:
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langchain_api_key)
    os.environ.setdefault(
        "LANGCHAIN_TRACING_V2",
        "true" if settings.langchain_tracing_v2 else "false",
    )
    os.environ.setdefault("LANGCHAIN_PROJECT", settings.langchain_project)

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY (or GEMINI_API_KEY) is missing. "
            "Copy .env.example to .env and set it."
        )

    model = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        temperature=0,
        google_api_key=api_key,
    )

    tools = [
        get_flights,
        get_hotels,
        book_flight,
        book_hotel,
        cancel_booking,
    ]

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=TRAVEL_AGENT_SYSTEM_PROMPT,
    )
