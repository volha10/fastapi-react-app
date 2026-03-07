from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Request, HTTPException, status, Depends, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import EmailStr
from pymongo import errors
from pwdlib import PasswordHash

from app.auth.models import JwtTokenType
from app.auth.schemas import (
    RefreshOut,
    User,
    UserOut,
    UserSignin,
    UserSigninOut,
    UserSignup,
)

APP_JWT_ALG = "HS256"
APP_JWT_SECRET = "secret"
APP_JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
APP_JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

router = APIRouter(prefix="/api/v1/users", tags=["users"])

oath2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/signin")
password_hash = PasswordHash.recommended()

RefreshTokenHeader = Annotated[str, Header(alias="X-Refresh-Token")]


def generate_token(
    email: EmailStr, expires_delta: timedelta, token_type: JwtTokenType
) -> str:
    now = datetime.now(timezone.utc)
    exp = now + expires_delta

    token = jwt.encode(
        {"email": email, "exp": exp, "type": token_type},
        key=APP_JWT_SECRET,
        algorithm=APP_JWT_ALG,
    )

    return token


def verify_token(token: str) -> dict | None:
    try:
        payload: dict = jwt.decode(token, key=APP_JWT_SECRET, algorithms=[APP_JWT_ALG])
        print(payload)
    except (jwt.ExpiredSignatureError, jwt.exceptions.InvalidSignatureError) as error:
        print(error)
        return None

    return payload


async def get_current_user(
    request: Request, token: str = Depends(oath2_scheme)
) -> User:
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
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


@router.post("/signin", response_model=UserSigninOut)
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

    access_token = generate_token(
        user_in.email,
        timedelta(minutes=APP_JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        JwtTokenType.ACCESS,
    )
    refresh_token = generate_token(
        user_in.email,
        timedelta(days=APP_JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        JwtTokenType.REFRESH,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }


@router.post("/refresh")
def refresh(refresh_token: RefreshTokenHeader) -> RefreshOut:
    payload = verify_token(refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )

    sub = payload["email"]

    new_access_token = generate_token(
        sub,
        expires_delta=timedelta(minutes=APP_JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type=JwtTokenType.ACCESS,
    )

    new_refresh_token = generate_token(
        sub,
        expires_delta=timedelta(days=APP_JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        token_type=JwtTokenType.REFRESH,
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "Bearer",
    }


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
