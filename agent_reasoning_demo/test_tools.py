from tools import (
    search_knowledge_base,
    get_user_details,
    check_ticket_status,
    create_ticket
)


print("=" * 60)
print("KNOWLEDGE BASE")
print("=" * 60)

result = search_knowledge_base.invoke({
    "query": "VPN is not working"
})

print(result)


print("\n" + "=" * 60)
print("USER DETAILS")
print("=" * 60)

result = get_user_details.invoke({
    "employee_id": "ABC123"
})

print(result)


print("\n" + "=" * 60)
print("TICKET STATUS")
print("=" * 60)

result = check_ticket_status.invoke({
    "ticket_id": "INC-1001"
})

print(result)


print("\n" + "=" * 60)
print("CREATE TICKET")
print("=" * 60)

result = create_ticket.invoke({
    "issue": "VPN is not connecting"
})

print(result)