from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.auth import service
from app.auth.models import JwtTokenType, UserPayload
from app.auth.repositories import (
    AbstractRefreshTokenRepository,
    AbstractUserRepository,
    MongoRefreshTokenRepository,
    UserRepository,
)
from app.auth.schemas import User

oath2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/signin")
RefreshTokenHeader = Annotated[str, Header(alias="X-Refresh-Token")]


def get_user_repository(request: Request) -> AbstractUserRepository:
    return UserRepository(request.app.state.db)


async def get_current_user(
    token: str = Depends(oath2_scheme),
    repo: AbstractUserRepository = Depends(get_user_repository),
) -> User:
    payload = service.verify_token(token, expected_token_type=JwtTokenType.ACCESS)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )

    found_result: User | None = await repo.get(payload.email)

    if not found_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return found_result


def get_refresh_token_data(
    refresh_token: RefreshTokenHeader,
) -> tuple[UserPayload, str]:
    payload = service.verify_token(
        refresh_token, expected_token_type=JwtTokenType.REFRESH
    )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )

    return payload, refresh_token


def get_refresh_token_repository(request: Request) -> AbstractRefreshTokenRepository:
    return MongoRefreshTokenRepository(request.app.state.db)
