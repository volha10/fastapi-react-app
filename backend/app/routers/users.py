from typing import Annotated
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field
from pymongo import errors

router = APIRouter(prefix="/api/v1/users", tags=["users"])


StrObjectId = Annotated[str, BeforeValidator(str)]

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str


class User(BaseModel):
    # validation_alias = read from DB as '_id'
    # field name 'id' = output to JSON as 'id'
    id: StrObjectId = Field(validation_alias="_id")
    name: str
    email: EmailStr
    password: str 

    model_config = ConfigDict(
        populate_by_name=True, 
    )   

4
@router.post("/signup")
async def signup(request: Request, user: UserSignup) -> User:
    try:
        insert_result = await request.app.state.db["users"].insert_one(user.model_dump())
        
        new_user = await request.app.state.db["users"].find_one({"_id": insert_result.inserted_id})

        print(f"New user {new_user} created successfully")
    except errors.DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    return new_user
