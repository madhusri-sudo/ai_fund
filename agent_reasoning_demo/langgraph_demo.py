from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END
)


# ---------------------------------------------------------
# State
# ---------------------------------------------------------

class SupportState(TypedDict):

    user_query: str
    category: str
    response: str


# ---------------------------------------------------------
# Classify request
# ---------------------------------------------------------

def classify_request(state: SupportState):

    query = state["user_query"].lower()

    if "vpn" in query:

        category = "vpn"

    elif "password" in query:

        category = "password"

    elif "email" in query:

        category = "email"

    elif "ticket" in query:

        category = "ticket"

    else:

        category = "unknown"

    return {
        "category": category
    }


# ---------------------------------------------------------
# VPN handler
# ---------------------------------------------------------

def handle_vpn(state: SupportState):

    return {
        "response": (
            "For VPN issues, check your internet connection, "
            "restart the VPN client, verify your credentials, "
            "and try reconnecting."
        )
    }


# ---------------------------------------------------------
# Password handler
# ---------------------------------------------------------

def handle_password(state: SupportState):

    return {
        "response": (
            "Use the company password portal, select "
            "Forgot Password, verify your employee ID, "
            "and create a new password."
        )
    }


# ---------------------------------------------------------
# Email handler
# ---------------------------------------------------------

def handle_email(state: SupportState):

    return {
        "response": (
            "For email problems, restart Outlook, "
            "check your internet connection, verify your "
            "credentials, and check mailbox capacity."
        )
    }


# ---------------------------------------------------------
# Ticket handler
# ---------------------------------------------------------

def handle_ticket(state: SupportState):

    return {
        "response": (
            "Please provide the ticket ID so that "
            "the ticket status can be checked."
        )
    }


# ---------------------------------------------------------
# Unknown handler
# ---------------------------------------------------------

def handle_unknown(state: SupportState):

    return {
        "response": (
            "I need a little more information to understand "
            "your IT support issue."
        )
    }


# ---------------------------------------------------------
# Conditional routing
# ---------------------------------------------------------

def route_request(state: SupportState):

    category = state["category"]

    if category == "vpn":
        return "vpn"

    if category == "password":
        return "password"

    if category == "email":
        return "email"

    if category == "ticket":
        return "ticket"

    return "unknown"


# ---------------------------------------------------------
# Create graph
# ---------------------------------------------------------

graph_builder = StateGraph(SupportState)


graph_builder.add_node(
    "classify",
    classify_request
)

graph_builder.add_node(
    "vpn",
    handle_vpn
)

graph_builder.add_node(
    "password",
    handle_password
)

graph_builder.add_node(
    "email",
    handle_email
)

graph_builder.add_node(
    "ticket",
    handle_ticket
)

graph_builder.add_node(
    "unknown",
    handle_unknown
)


# ---------------------------------------------------------
# Edges
# ---------------------------------------------------------

graph_builder.add_edge(
    START,
    "classify"
)


graph_builder.add_conditional_edges(
    "classify",
    route_request,
    {
        "vpn": "vpn",
        "password": "password",
        "email": "email",
        "ticket": "ticket",
        "unknown": "unknown"
    }
)


graph_builder.add_edge(
    "vpn",
    END
)

graph_builder.add_edge(
    "password",
    END
)

graph_builder.add_edge(
    "email",
    END
)

graph_builder.add_edge(
    "ticket",
    END
)

graph_builder.add_edge(
    "unknown",
    END
)


# ---------------------------------------------------------
# Compile
# ---------------------------------------------------------

graph = graph_builder.compile()


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    query = input("User: ")

    result = graph.invoke(
        {
            "user_query": query,
            "category": "",
            "response": ""
        }
    )

    print("\nAssistant:")
    print(result["response"])