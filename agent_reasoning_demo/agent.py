import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from tools import tools


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Create model
# ---------------------------------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0
)


# ---------------------------------------------------------
# Agent instructions
# ---------------------------------------------------------

system_prompt = """
You are an IT support assistant.

You can help users with:

- VPN problems
- Password problems
- Email problems
- Laptop problems
- User information
- Existing support tickets
- Creating support tickets

Use tools whenever you need information or need to perform
an action.

Do not invent information.

If the user asks for troubleshooting information,
search the knowledge base.

If the user asks about a ticket,
check the ticket status.

If the user provides an employee ID and asks for user details,
use the user details tool.

Only create a ticket when the user explicitly asks for
a support ticket or when the user's request clearly requires
ticket creation.

Give a concise and useful final answer.
"""


# ---------------------------------------------------------
# Create agent
# ---------------------------------------------------------

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt
)


# ---------------------------------------------------------
# Helper function
# ---------------------------------------------------------

def print_agent_response(response):

    """
    Extract only text from the agent response.
    """

    if isinstance(response, str):
        print(response)
        return

    if isinstance(response, list):

        for item in response:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):
                print(item.get("text", ""))

        return

    print(response)


# # ---------------------------------------------------------
# # Run one request
# # ---------------------------------------------------------

# response = agent.invoke(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "My VPN is not working."
#             }
#         ]
#     }
# )


# # ---------------------------------------------------------
# # Extract final AI message
# # ---------------------------------------------------------

# messages = response["messages"]

# final_message = messages[-1]

# content = final_message.content

# if isinstance(content, str):

#     print(content)

# elif isinstance(content, list):

#     for item in content:

#         if (
#             isinstance(item, dict)
#             and item.get("type") == "text"
#         ):
#             print(item["text"])

while True:

    user_input = input("\nYou: ")

    if user_input.lower() in {
        "exit",
        "quit",
        "bye"
    }:
        print("Goodbye!")
        break

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }
    )

    final_message = response["messages"][-1]

    content = final_message.content

    if isinstance(content, str):

        print("\nAssistant:")
        print(content)

    elif isinstance(content, list):

        print("\nAssistant:")

        for item in content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):
                print(item["text"])