from fastapi import FastAPI, Query, Request
import httpx
from src.utils.cache import SimpleCache
from src import auth
from collections import Counter
from fastapi.responses import JSONResponse
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()
cache = SimpleCache()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"message": "Previše zahtjeva, pokušajte ponovno kasnije."},
    )

async def fetch_tickets():
    url = "https://dummyjson.com/todos"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        tickets = []
        for item in data["todos"]:
            ticket = {
                "id": item["id"],
                "title": item["todo"],
                "status": "closed" if item["completed"] else "open",
                "priority": ["low", "medium", "high"][item["id"] % 3],
                "description": item["todo"][:100],
                "userId": item["userId"]
            }
            tickets.append(ticket)
        return tickets

@app.get("/tickets")
@limiter.limit("10/minute")
async def get_tickets(request: Request, status: str | None = Query(None), priority: str | None = Query(None)):
    logger.info("Pozvan GET /tickets endpoint")
    
    cache_key = f"tickets_{status}_{priority}"
    cached = cache.get(cache_key)
    if cached:
        logger.info("Vraćam tickete iz cachea")
        return cached

    tickets = await fetch_tickets()

    if status:
        tickets = [t for t in tickets if t["status"] == status]
    if priority:
        tickets = [t for t in tickets if t["priority"] == priority]

    cache.set(cache_key, tickets, ttl=60) 
    logger.info("Vraćam listu ticketa nakon filtriranja")
    return tickets


@app.get("/stats")
async def get_ticket_stats():
    cache_key = "ticket_stats"
    cached = cache.get(cache_key)
    if cached:
        return JSONResponse(content=cached)

    tickets = await fetch_tickets()
    
    total = len(tickets)
    status_count = Counter([t["status"] for t in tickets])
    priority_count = Counter([t["priority"] for t in tickets])

    stats = {
        "total_tickets": total,
        "status": status_count,
        "priority": priority_count
    }

    cache.set(cache_key, stats, ttl=60)
    return JSONResponse(content=stats)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(auth.router)
