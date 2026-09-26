import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# KNOWLEDGE BASE
# =========================================================

knowledge_base = {

    "vpn": """
    VPN Troubleshooting Guide

    If VPN is not working:

    - Check internet connectivity.
    - Restart the VPN client.
    - Verify username and password.
    - Disconnect and reconnect.
    - Try another VPN server.
    - Restart the laptop.
    - Create an IT support ticket if the issue continues.
    """,

    "password": """
    Password Reset Guide

    - Open the company password portal.
    - Select Forgot Password.
    - Enter employee ID.
    - Verify identity.
    - Create a new password.
    - Log in again.
    """,

    "email": """
    Email Troubleshooting Guide

    - Check internet connection.
    - Restart Outlook.
    - Verify credentials.
    - Check mailbox capacity.
    - Check company service status.
    """
}


# =========================================================
# USERS
# =========================================================

users = {

    "ABC123": {
        "name": "John",
        "department": "Engineering",
        "email": "john@company.com"
    },

    "USER456": {
        "name": "Sarah",
        "department": "Finance",
        "email": "sarah@company.com"
    }
}


# =========================================================
# TICKETS
# =========================================================

tickets = {

    "INC-1001": {
        "issue": "VPN connection problem",
        "status": "In Progress",
        "priority": "High"
    },

    "INC-1005": {
        "issue": "Email not working",
        "status": "Open",
        "priority": "Medium"
    }
}


# =========================================================
# TOOL — SEARCH KNOWLEDGE BASE
# =========================================================

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the company IT support knowledge base.
    """

    query = query.lower()

    matched = []

    for topic, content in knowledge_base.items():

        if topic in query:

            matched.append(content)

    if not matched:

        return (
            "No relevant knowledge base information "
            "was found."
        )

    return "\n\n".join(matched)


# =========================================================
# TOOL — USER DETAILS
# =========================================================

@tool
def get_user_details(employee_id: str) -> str:
    """
    Get user information using employee ID.
    """

    user = users.get(employee_id)

    if not user:

        return (
            f"No employee was found with ID "
            f"{employee_id}."
        )

    return (
        f"Employee ID: {employee_id}\n"
        f"Name: {user['name']}\n"
        f"Department: {user['department']}\n"
        f"Email: {user['email']}"
    )


# =========================================================
# TOOL — CHECK TICKET
# =========================================================

@tool
def check_ticket_status(ticket_id: str) -> str:
    """
    Check the status of an existing support ticket.
    """

    ticket = tickets.get(ticket_id)

    if not ticket:

        return (
            f"Ticket {ticket_id} does not exist."
        )

    return (
        f"Ticket ID: {ticket_id}\n"
        f"Issue: {ticket['issue']}\n"
        f"Status: {ticket['status']}\n"
        f"Priority: {ticket['priority']}"
    )


# =========================================================
# TOOL — CREATE TICKET
# =========================================================

@tool
def create_ticket(issue: str) -> str:
    """
    Create a new IT support ticket.
    """

    numbers = []

    for ticket_id in tickets:

        try:

            numbers.append(
                int(ticket_id.split("-")[1])
            )

        except ValueError:

            pass

    next_number = (
        max(numbers) + 1
        if numbers
        else 1001
    )

    ticket_id = f"INC-{next_number}"

    tickets[ticket_id] = {

        "issue": issue,

        "status": "Open",

        "priority": "Medium"
    }

    return (
        f"Ticket created successfully.\n"
        f"Ticket ID: {ticket_id}\n"
        f"Issue: {issue}\n"
        f"Status: Open\n"
        f"Priority: Medium"
    )


# =========================================================
# TOOLS
# =========================================================

tools = [

    search_knowledge_base,

    get_user_details,

    check_ticket_status,

    create_ticket
]


# =========================================================
# MODEL
# =========================================================

model = ChatGoogleGenerativeAI(

    model="gemini-3.5-flash",

    temperature=0
)


# =========================================================
# SYSTEM PROMPT
# =========================================================

system_prompt = """

You are an enterprise IT support assistant.

You have access to four tools:

1. search_knowledge_base
2. get_user_details
3. check_ticket_status
4. create_ticket

Use search_knowledge_base for troubleshooting questions.

Use get_user_details when the user provides an employee ID
and requests employee information.

Use check_ticket_status when the user asks about an
existing ticket.

Use create_ticket when the user explicitly asks to create
a support ticket.

Never invent company information.

Use tool results as the source of truth.

Do not expose internal reasoning.

Give a concise final answer.

If troubleshooting steps are available, provide them clearly.

If a ticket is created, provide the ticket ID and status.

"""


# =========================================================
# CREATE AGENT
# =========================================================

agent = create_agent(

    model=model,

    tools=tools,

    system_prompt=system_prompt
)


# =========================================================
# EXTRACT TEXT
# =========================================================

def extract_text(message):

    content = message.content

    if isinstance(content, str):

        return content

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):

                text_parts.append(
                    item.get("text", "")
                )

        return "\n".join(text_parts)

    return str(content)


# =========================================================
# RUN AGENT
# =========================================================

def ask_agent(query):

    response = agent.invoke({

        "messages": [

            {
                "role": "user",

                "content": query
            }
        ]
    })

    final_message = response["messages"][-1]

    return extract_text(final_message)


# =========================================================
# TEST EXAMPLES
# =========================================================

if __name__ == "__main__":

    print("=" * 70)

    print("IT SUPPORT AGENT")

    print("=" * 70)


    examples = [

        "My VPN is not working.",

        "How do I reset my password?",

        "What is the status of INC-1001?",

        "My employee ID is ABC123. What are my details?",

        "Create a support ticket because my VPN is not working.",

        "My employee ID is ABC123. Check my details and investigate my VPN issue."

    ]


    for query in examples:

        print("\n" + "-" * 70)

        print("USER:")

        print(query)

        print("\nASSISTANT:")

        try:

            answer = ask_agent(query)

            print(answer)

        except Exception as e:

            print(
                f"Error while processing request: {e}"
            )


# =========================================================
# INTERACTIVE MODE
# =========================================================

def interactive_mode():

    print("\nInteractive mode")

    print("Type 'exit' to stop.\n")


    while True:

        query = input("You: ")

        if query.lower() in {

            "exit",

            "quit",

            "bye"
        }:

            print("Goodbye!")

            break


        try:

            answer = ask_agent(query)

            print("\nAssistant:")

            print(answer)

        except Exception as e:

            print(
                f"\nError: {e}"
            )