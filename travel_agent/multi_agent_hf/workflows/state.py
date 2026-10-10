"""Shared state definitions for travel multi-agent workflows."""

from __future__ import annotations

from typing import Literal, TypedDict


class TravelState(TypedDict, total=False):
    """Shared workspace passed between nodes in sequential workflow."""

    request: str
    flights: str
    hotels: str
    itinerary: str
    final_answer: str


class SupervisorState(TypedDict, total=False):
    """Shared workspace for supervisor-driven orchestration."""

    request: str
    flights: str
    hotels: str
    itinerary: str
    final_answer: str
    next_agent: Literal["flight", "hotel", "itinerary", "final_answer", "FINISH"]
    steps: list[str]
