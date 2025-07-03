import httpx
from src.models.ticket import Ticket, TicketPriority, TicketStatus

async def fetch_tickets():
    async with httpx.AsyncClient() as client:
        todos_resp = await client.get("https://dummyjson.com/todos")
        users_resp = await client.get("https://dummyjson.com/users")

    todos = todos_resp.json()["todos"]
    users = {user["id"]: user["username"] for user in users_resp.json()["users"]}

    def map_priority(ticket_id: int) -> TicketPriority:
        return [TicketPriority.low, TicketPriority.medium, TicketPriority.high][ticket_id % 3]

    ticket_list = [
        Ticket(
            id=t["id"],
            title=t["todo"],
            status=TicketStatus.closed if t["completed"] else TicketStatus.open,
            priority=map_priority(t["id"]),
            assignee=users.get(t["userId"], "unknown")
        )
        for t in todos
    ]
    return ticket_list
