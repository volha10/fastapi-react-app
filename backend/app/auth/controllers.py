from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import service
from app.auth.dependencies import (
    get_current_user,
    get_refresh_token_payload,
    get_user_repository,
)
from app.auth.models import UserPayload
from app.auth.repository import AbstractUserRepository
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
    repo: AbstractUserRepository = Depends(get_user_repository),
) -> UserSigninOut:
    user_in = UserSignin(email=form_data.username, password=form_data.password)

    found_result = await service.authenticate_user(user_in, repo)

    if not found_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return UserSigninOut(**service.create_user_tokens(user_in.email))


@router.post("/refresh")
def refresh(payload: UserPayload = Depends(get_refresh_token_payload)) -> RefreshOut:
    return RefreshOut(**service.create_user_tokens(payload.email))


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(**current_user.model_dump())
