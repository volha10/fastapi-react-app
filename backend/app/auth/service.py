from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.auth.exceptions import TokenReuseError
from app.auth.models import JwtTokenType, UserPayload
from app.auth.repositories import AbstractRefreshTokenRepository, AbstractUserRepository
from app.auth.schemas import (
    User,
    UserSignin,
    UserSignup,
)
from app.core.config import settings

password_hash = PasswordHash.recommended()


async def register_user(
    user_in: UserSignup, repo: AbstractUserRepository
) -> dict | None:
    hash = password_hash.hash(user_in.password)

    hashed_user = UserSignup(**user_in.model_dump(exclude={"password"}), password=hash)

    new_user = await repo.create(hashed_user.model_dump())

    return new_user


async def authenticate_user(
    user_in: UserSignin, repo: AbstractUserRepository
) -> User | None:
    found_user = await repo.get_by_email(user_in.email)

    if not found_user or not password_hash.verify(
        user_in.password, found_user.password_hash
    ):
        return None

    return found_user


async def create_user_tokens(
    user_id: str, token_repo: AbstractRefreshTokenRepository
) -> dict:
    access_token = generate_token(
        user_id,
        timedelta(minutes=settings.APP_JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        JwtTokenType.ACCESS,
    )
    refresh_token = generate_token(
        user_id,
        timedelta(days=settings.APP_JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        JwtTokenType.REFRESH,
    )

    expired_at = datetime.now(timezone.utc) + timedelta(
        days=settings.APP_JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    await token_repo.create(user_id, refresh_token, expired_at)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }


def generate_token(
    user_id: str, expires_delta: timedelta, token_type: JwtTokenType
) -> str:
    now = datetime.now(timezone.utc)
    exp = now + expires_delta

    token = jwt.encode(
        {"sub": user_id, "exp": exp, "type": token_type},
        key=settings.APP_JWT_SECRET,
        algorithm=settings.APP_JWT_ALG,
    )

    return token


def verify_token(token: str, expected_token_type: JwtTokenType) -> UserPayload | None:
    try:
        payload: dict = jwt.decode(
            token, key=settings.APP_JWT_SECRET, algorithms=[settings.APP_JWT_ALG]
        )
        print(payload)

        user_payload = UserPayload(**payload)

        if user_payload.type != expected_token_type:
            return None

        return user_payload
    except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError) as error:
        print(error)
        return None


async def rotate_tokens(
    payload: UserPayload, refresh_token: str, token_repo: AbstractRefreshTokenRepository
) -> dict:
    is_deleted = await token_repo.is_found_and_deleted(payload.sub, refresh_token)

    if not is_deleted:
        token_repo.revoke_all(user_id=payload.sub)
        raise TokenReuseError()

    tokens = await create_user_tokens(payload.sub, token_repo)

    return tokens


async def logout(
    sub: str, refresh_token: str, token_repo: AbstractRefreshTokenRepository
) -> None:
    await token_repo.is_found_and_deleted(sub, refresh_token)
