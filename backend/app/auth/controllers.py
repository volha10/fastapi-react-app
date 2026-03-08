from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash

from app.auth import service
from app.auth.dependencies import get_user_repository
from app.auth.repository import UserRepository
from app.auth.schemas import (
    RefreshOut,
    User,
    UserOut,
    UserSignin,
    UserSigninOut,
    UserSignup,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])

oath2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/signin")
password_hash = PasswordHash.recommended()

RefreshTokenHeader = Annotated[str, Header(alias="X-Refresh-Token")]


async def get_current_user(
    request: Request, token: str = Depends(oath2_scheme)
) -> User:
    payload = service.verify_token(token)

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
async def signup(
    user_in: UserSignup, repo: UserRepository = Depends(get_user_repository)
):
    hash = password_hash.hash(user_in.password)

    hashed_user = UserSignup(**user_in.model_dump(exclude={"password"}), password=hash)

    new_user = await repo.create(hashed_user.model_dump())

    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this email already exists",
        )

    return new_user


@router.post("/signin", response_model=UserSigninOut)
async def signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: UserRepository = Depends(get_user_repository),
):
    user_in = UserSignin(email=form_data.username, password=form_data.password)

    found_result = await service.authenticate_user(user_in, repo)

    if not found_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return service.create_user_tokens(user_in.email)


@router.post("/refresh")
def refresh(refresh_token: RefreshTokenHeader) -> RefreshOut:
    payload = service.verify_token(refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )

    sub = payload["email"]

    return service.create_user_tokens(sub)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
