from pydantic import BaseModel
from enum import Enum


class TicketStatus(str, Enum):
    open = "open"
    closed = "closed"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Ticket(BaseModel):
    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    assignee: str
