from tools import (
    search_knowledge_base,
    check_ticket_status,
    create_ticket
)


# ---------------------------------------------------------
# Example: LLM decides that knowledge base is required
# ---------------------------------------------------------

tool_name = "search_knowledge_base"

tool_arguments = {
    "query": "VPN is not working"
}


if tool_name == "search_knowledge_base":

    result = search_knowledge_base.invoke(
        tool_arguments
    )

    print(result)


# ---------------------------------------------------------
# Example: LLM decides that ticket status is required
# ---------------------------------------------------------

tool_name = "check_ticket_status"

tool_arguments = {
    "ticket_id": "INC-1001"
}


if tool_name == "check_ticket_status":

    result = check_ticket_status.invoke(
        tool_arguments
    )

    print("\n")
    print(result)


# ---------------------------------------------------------
# Example: LLM decides to create ticket
# ---------------------------------------------------------

tool_name = "create_ticket"

tool_arguments = {
    "issue": "VPN connection failure"
}


if tool_name == "create_ticket":

    result = create_ticket.invoke(
        tool_arguments
    )

    print("\n")
    print(result)