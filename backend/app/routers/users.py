from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


@router.post("/signup")
def signup(user: UserCreate):
    return {"message": "User successfully signed up", "result": user.model_dump()}
