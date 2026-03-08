from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from pydantic import EmailStr

from app.auth.models import JwtTokenType
from app.auth.repository import UserRepository
from app.auth.schemas import (
    UserSignin,
    UserSignup,
)
from app.core.config import settings

password_hash = PasswordHash.recommended()


async def register_user(user_in: UserSignup, repo: UserRepository):
    hash = password_hash.hash(user_in.password)

    hashed_user = UserSignup(**user_in.model_dump(exclude={"password"}), password=hash)

    new_user = await repo.create(hashed_user.model_dump())

    return new_user


async def authenticate_user(user_in: UserSignin, repo: UserRepository) -> dict:
    found_result = await repo.get(user_in.email)

    if not found_result or not password_hash.verify(
        user_in.password, found_result["password"]
    ):
        return None

    return found_result


def create_user_tokens(email: EmailStr) -> dict:
    access_token = generate_token(
        email,
        timedelta(minutes=settings.APP_JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        JwtTokenType.ACCESS,
    )
    refresh_token = generate_token(
        email,
        timedelta(days=settings.APP_JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        JwtTokenType.REFRESH,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }


def generate_token(
    email: EmailStr, expires_delta: timedelta, token_type: JwtTokenType
) -> str:
    now = datetime.now(timezone.utc)
    exp = now + expires_delta

    token = jwt.encode(
        {"email": email, "exp": exp, "type": token_type},
        key=settings.APP_JWT_SECRET,
        algorithm=settings.APP_JWT_ALG,
    )

    return token


def verify_token(token: str) -> dict | None:
    try:
        payload: dict = jwt.decode(
            token, key=settings.APP_JWT_SECRET, algorithms=[settings.APP_JWT_ALG]
        )
        print(payload)
    except (jwt.ExpiredSignatureError, jwt.exceptions.InvalidSignatureError) as error:
        print(error)
        return None

    return payload
