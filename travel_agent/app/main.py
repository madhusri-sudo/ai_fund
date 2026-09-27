"""CLI chat interface for the travel agent."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python app/main.py` from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from app.agent.travel_agent import build_travel_agent


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(part for part in parts if part)

    return str(content)


def main() -> None:
    print("Travel Agent CLI")
    print("Type 'exit', 'quit', or 'bye' to leave.\n")

    agent = build_travel_agent()
    messages: list[dict] = []

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            response = agent.invoke({"messages": messages})
        except Exception as exc:
            print(f"\nAssistant:\nError: {exc}\n")
            messages.pop()
            continue

        final_message = response["messages"][-1]
        text = _extract_text(final_message.content)

        # Keep conversation history for multi-turn booking flows.
        messages = response["messages"]

        print("\nAssistant:")
        print(text)
        print()


if __name__ == "__main__":
    main()
