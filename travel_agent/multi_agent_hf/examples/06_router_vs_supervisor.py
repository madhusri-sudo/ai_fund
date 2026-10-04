"""
Topic: Router vs Supervisor (mini conceptual demo).

Router: one-shot choose a specialist, then stop.
Supervisor: may call multiple specialists until FINISH.
"""

from __future__ import annotations


def router(query: str) -> str:
    q = query.lower()
    if "flight" in q and "hotel" not in q and "itinerary" not in q:
        return "flight"
    if "hotel" in q and "flight" not in q:
        return "hotel"
    if "itinerary" in q or "plan" in q:
        return "itinerary"
    return "flight"


def fake_supervisor_path(query: str) -> list[str]:
    q = query.lower()
    steps = ["supervisor"]
    if "flight" in q or "plan" in q or "trip" in q:
        steps += ["flight", "supervisor"]
    if "hotel" in q or "plan" in q or "trip" in q:
        steps += ["hotel", "supervisor"]
    if "itinerary" in q or "plan" in q or "trip" in q:
        steps += ["itinerary", "supervisor"]
    steps.append("FINISH")
    return steps


def main() -> None:
    samples = [
        "Find flights to Delhi",
        "Find hotels in Delhi",
        "Plan my full trip to Delhi",
    ]
    print("=== Router (one specialist) ===")
    for s in samples:
        print(f"  '{s}' → {router(s)}")

    print("\n=== Supervisor (possibly many specialists) ===")
    for s in samples:
        print(f"  '{s}' → {' → '.join(fake_supervisor_path(s))}")

    print(
        "\nNote: Router picks ONE path. "
        "Supervisor can coordinate MANY steps."
    )


if __name__ == "__main__":
    main()
