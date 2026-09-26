# ---------------------------------------------------------
# Simple IT Support Knowledge Base
# ---------------------------------------------------------

knowledge_base = {
    "vpn": """
    VPN Troubleshooting Guide

    If your VPN is not connecting:

    1. Check whether your internet connection is working.
    2. Restart the VPN client.
    3. Verify your username and password.
    4. Disconnect and reconnect the VPN.
    5. Try changing the VPN server or region.
    6. Restart your laptop.
    7. If the problem continues, create an IT support ticket.

    Common VPN errors:
    - Authentication failed
    - Connection timeout
    - Unable to reach VPN server
    - Invalid credentials
    """,

    "password": """
    Password Reset Guide

    If you forgot your company password:

    1. Open the company password portal.
    2. Click "Forgot Password".
    3. Enter your employee ID.
    4. Verify your identity.
    5. Enter a new password.
    6. Confirm the new password.
    7. Log in again using the new password.

    Password requirements:
    - At least 12 characters
    - One uppercase letter
    - One lowercase letter
    - One number
    - One special character
    """,

    "email": """
    Email Troubleshooting Guide

    If company email is not working:

    1. Check your internet connection.
    2. Restart Outlook or your email application.
    3. Check whether the mailbox is full.
    4. Re-enter your credentials.
    5. Check the company service status.
    6. Restart your computer.
    7. Create a support ticket if the problem continues.
    """,

    "laptop": """
    Laptop Troubleshooting Guide

    If your laptop is slow:

    1. Restart the laptop.
    2. Close unnecessary applications.
    3. Check available disk space.
    4. Check Task Manager for applications consuming high CPU.
    5. Install pending operating system updates.
    6. Run the approved antivirus scan.
    7. Contact IT support if the issue continues.
    """
}


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


next_ticket_number = 1006