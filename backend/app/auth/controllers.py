from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import service
from app.auth.dependencies import (
    get_current_user,
    get_refresh_token_data,
    get_refresh_token_repository,
    get_user_repository,
)
from app.auth.exceptions import TokenReuseError
from app.auth.models import UserPayload
from app.auth.repositories import AbstractRefreshTokenRepository, AbstractUserRepository
from app.auth.schemas import (
    RefreshOut,
    User,
    UserOut,
    UserSignin,
    UserSigninOut,
    UserSignup,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/signup")
async def signup(
    user_in: UserSignup, repo: AbstractUserRepository = Depends(get_user_repository)
) -> UserOut:
    new_user = await service.register_user(user_in, repo)

    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this email already exists",
        )

    return UserOut(**new_user)


@router.post("/signin")
async def signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: AbstractUserRepository = Depends(get_user_repository),
    token_repo: AbstractRefreshTokenRepository = Depends(
        dependency=get_refresh_token_repository
    ),
) -> UserSigninOut:
    user_in = UserSignin(email=form_data.username, password=form_data.password)

    found_user: User | None = await service.authenticate_user(user_in, user_repo)

    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    tokens = await service.create_user_tokens(found_user.id, token_repo)

    return UserSigninOut(**tokens)


@router.post("/refresh")
async def refresh(
    token_data: tuple[UserPayload, str] = Depends(get_refresh_token_data),
    token_repo: AbstractRefreshTokenRepository = Depends(get_refresh_token_repository),
) -> RefreshOut:
    payload, refresh_token = token_data

    try:
        new_tokens = await service.rotate_tokens(payload, refresh_token, token_repo)
    except TokenReuseError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security alert: Token reuse detected",
        )
    return RefreshOut(**new_tokens)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(**current_user.model_dump())


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token_data: tuple[UserPayload, str] = Depends(get_refresh_token_data),
    token_repo: AbstractRefreshTokenRepository = Depends(get_refresh_token_repository),
) -> None:
    user_payload, refresh_token  = token_data

    await service.logout(user_payload.sub, refresh_token, token_repo)
