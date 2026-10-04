"""Shared Gemini LLM helper for multi-agent demos."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(PROJECT_ROOT / ".env")

from app.config.settings import get_settings


def get_llm(temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    """Create a Gemini chat model using project settings."""
    settings = get_settings()
    api_key = settings.resolved_google_api_key or os.getenv("GOOGLE_API_KEY", "")

    if api_key:
        os.environ.setdefault("GOOGLE_API_KEY", api_key)
    if settings.langchain_api_key:
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langchain_api_key)
        os.environ.setdefault("LANGSMITH_API_KEY", settings.langchain_api_key)
    os.environ.setdefault(
        "LANGCHAIN_TRACING_V2",
        "true" if settings.langchain_tracing_v2 else "false",
    )
    os.environ.setdefault("LANGCHAIN_PROJECT", settings.langchain_project)
    os.environ.setdefault(
        "LANGSMITH_TRACING",
        "true" if settings.langchain_tracing_v2 else "false",
    )
    os.environ.setdefault("LANGSMITH_PROJECT", settings.langchain_project)

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY (or GEMINI_API_KEY) is missing. "
            "Copy .env.example to .env and set it."
        )

    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        temperature=temperature,
        google_api_key=api_key,
    )


def invoke_text(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """Simple one-shot LLM call that returns text."""
    llm = get_llm(temperature=temperature)
    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    content = response.content
    if isinstance(content, str):
        return content
    return str(content)
