import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: int
    username: str
    email: str
    token: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    url = "https://dummyjson.com/auth/login"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=request.dict())
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return response.json()
