from langchain.tools import tool

from data import (
    knowledge_base,
    users,
    tickets
)


# ---------------------------------------------------------
# Knowledge Base Search
# ---------------------------------------------------------

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the IT support knowledge base.

    Use this tool when the user asks about troubleshooting,
    company procedures, VPN, password, email, or laptop issues.
    """

    query_lower = query.lower()

    results = []

    for topic, content in knowledge_base.items():

        if topic in query_lower:
            results.append(content)

    if not results:
        for topic, content in knowledge_base.items():

            keywords = topic.split()

            if any(
                keyword in query_lower
                for keyword in keywords
            ):
                results.append(content)

    if not results:
        return "No matching information was found in the knowledge base."

    return "\n\n".join(results)


# ---------------------------------------------------------
# User Details
# ---------------------------------------------------------

@tool
def get_user_details(employee_id: str) -> str:
    """
    Get employee information using an employee ID.
    """

    user = users.get(employee_id)

    if not user:
        return f"No user was found with employee ID {employee_id}."

    return (
        f"Employee ID: {employee_id}\n"
        f"Name: {user['name']}\n"
        f"Department: {user['department']}\n"
        f"Email: {user['email']}"
    )


# ---------------------------------------------------------
# Ticket Status
# ---------------------------------------------------------

@tool
def check_ticket_status(ticket_id: str) -> str:
    """
    Check the status of an existing IT support ticket.
    """

    ticket = tickets.get(ticket_id)

    if not ticket:
        return f"Ticket {ticket_id} was not found."

    return (
        f"Ticket ID: {ticket_id}\n"
        f"Issue: {ticket['issue']}\n"
        f"Status: {ticket['status']}\n"
        f"Priority: {ticket['priority']}"
    )


# ---------------------------------------------------------
# Create Ticket
# ---------------------------------------------------------

@tool
def create_ticket(issue: str) -> str:
    """
    Create a new IT support ticket.

    Use this tool when the user explicitly requests
    ticket creation.
    """

    next_number = 1006

    existing_numbers = []

    for ticket_id in tickets:
        try:
            number = int(ticket_id.split("-")[1])
            existing_numbers.append(number)
        except ValueError:
            pass

    if existing_numbers:
        next_number = max(existing_numbers) + 1

    ticket_id = f"INC-{next_number}"

    tickets[ticket_id] = {
        "issue": issue,
        "status": "Open",
        "priority": "Medium"
    }

    return (
        f"Your IT support ticket has been created.\n\n"
        f"Ticket ID: {ticket_id}\n"
        f"Issue: {issue}\n"
        f"Status: Open\n"
        f"Priority: Medium"
    )


# ---------------------------------------------------------
# Export tools
# ---------------------------------------------------------

tools = [
    search_knowledge_base,
    get_user_details,
    check_ticket_status,
    create_ticket
]