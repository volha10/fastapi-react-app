from typing import Annotated

from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field
from pymongo import errors
from pwdlib import PasswordHash

router = APIRouter(prefix="/api/v1/users", tags=["users"])


StrObjectId = Annotated[str, BeforeValidator(str)]


class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserSignin(BaseModel):
    email: EmailStr
    password: str


class UserBase(BaseModel):
    # validation_alias = read from DB as '_id'
    # field name 'id' = output to JSON as 'id'
    id: StrObjectId = Field(validation_alias="_id")
    name: str
    email: EmailStr

    model_config = ConfigDict(
        populate_by_name=True,
    )


class User(UserBase):
    password: str


class UserResponse(UserBase):
    pass


password_hash = PasswordHash.recommended()


@router.post("/signup", response_model=UserResponse)
async def signup(request: Request, user_in: UserSignup):
    try:
        hash = password_hash.hash(user_in.password)

        hashed_user = UserSignup(
            **user_in.model_dump(exclude={"password"}), password=hash
        )

        insert_result = await request.app.state.db["users"].insert_one(
            hashed_user.model_dump()
        )

        new_user = await request.app.state.db["users"].find_one(
            {"_id": insert_result.inserted_id}
        )

        print(f"New user {new_user} created successfully")
    except errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this email already exists",
        )

    return new_user


@router.post("/signin", response_model=UserResponse)
async def signin(request: Request, user_in: UserSignin):
    found_result: dict = await request.app.state.db["users"].find_one(
        {"email": user_in.email}
    )

    if not found_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect email or password"
        )

    user = User(**found_result)

    if not password_hash.verify(user_in.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect email or password"
        )

    return user
