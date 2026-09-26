from langchain.tools import tool

from tools import create_ticket


@tool
def create_ticket_with_approval(issue: str) -> str:
    """
    Create a support ticket after getting user approval.
    """

    print("\nTicket creation requested.")

    print(f"Issue: {issue}")

    approval = input(
        "Approve ticket creation? (yes/no): "
    )

    if approval.lower() != "yes":

        return "Ticket creation was cancelled by the user."

    result = create_ticket.invoke({
        "issue": issue
    })

    return result


@tool
def company_rag_search(query: str) -> str:
    """
    Search the company knowledge base using vector retrieval.
    """

    results = retriever.retrieve(query)

    context = []

    for result in results:

        text = result.node.get_content()

        context.append(text)

    return "\n\n".join(context)