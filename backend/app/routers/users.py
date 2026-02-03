from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field
from pymongo import errors
from pwdlib import PasswordHash

APP_JWT_ALG = "HS256"
APP_JWT_SECRET = "secret"
APP_JWT_EXP = 60 * 60

router = APIRouter(prefix="/api/v1/users", tags=["users"])


StrObjectId = Annotated[str, BeforeValidator(str)]


class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserSignin(BaseModel):
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


class UserOut(BaseModel):
    id: StrObjectId = Field(validation_alias="_id")
    name: str
    email: EmailStr

    model_config = ConfigDict(
        populate_by_name=True,
    )


class UserSigninOut(BaseModel):
    access_token: str


oath2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/signin")
password_hash = PasswordHash.recommended()


def generate_token(emal: EmailStr) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=APP_JWT_EXP)

    token = jwt.encode(
        {"email": emal, "exp": exp}, key=APP_JWT_SECRET, algorithm=APP_JWT_ALG
    )

    return token


async def get_current_user(
    request: Request, token: str = Depends(oath2_scheme)
) -> User:
    try:
        payload = jwt.decode(token, key=APP_JWT_SECRET, algorithms=[APP_JWT_ALG])
        print(payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )

    found_result: dict = await request.app.state.db["users"].find_one(
        {"email": payload["email"]}
    )

    if not found_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return User(**found_result)


@router.post("/signup", response_model=UserOut)
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


@router.post("/signin", response_model=UserSigninOut, include_in_schema=False)
async def signin(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user_in = UserSignin(email=form_data.username, password=form_data.password)
    found_result: dict = await request.app.state.db["users"].find_one(
        {"email": user_in.email}
    )

    if not found_result or not password_hash.verify(
        user_in.password, found_result["password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = generate_token(user_in.email)

    return {"access_token": token}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
