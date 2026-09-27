from langchain.tools import tool

knowledge_base = {
    "vpn": """
    VPN Troubleshooting Guide:
    1. Check your internet connection.
    2. Restart the VPN client.
    3. Verify your company credentials.
    4. Disconnect and reconnect.
    5. Restart your laptop.
    If the problem continues, contact IT support.
    """,
    "password": """
    Password Reset Guide:
    1. Open the Employee Access Portal.
    2. Click Forgot Password.
    3. Enter your employee ID.
    4. Verify the OTP.
    5. Create a new password.
    """
}

@tool("knowledge_base_search",)
def search_knowledge_base(query):
    query = query.lower()
    for key, value in knowledge_base.items():
        if key in query:
            return value
    return "No relevant article found."

# result = search_knowledge_base(
#     "My VPN is not working"
# )
# print(result)
