from fastapi import APIRouter
from typing import List
from src.models.ticket import Ticket
from src.services.tickets import fetch_tickets
from fastapi import Query
from typing import Optional

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("/", response_model=List[Ticket])
async def list_tickets(
    status: Optional[str] = Query(None, regex="^(open|closed)$"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    skip: int = 0,
    limit: int = 10
):
    tickets = await fetch_tickets()

    if status:
        tickets = [t for t in tickets if t.status == status]
    if priority:
        tickets = [t for t in tickets if t.priority == priority]

    return tickets[skip : skip + limit]

@router.get("/search", response_model=List[Ticket])
async def search_tickets(q: str):
    tickets = await fetch_tickets()
    q_lower = q.lower()
    return [t for t in tickets if q_lower in t.title.lower()]

@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: int):
    tickets = await fetch_tickets()
    ticket = next((t for t in tickets if t.id == ticket_id), None)
    if not ticket:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket




