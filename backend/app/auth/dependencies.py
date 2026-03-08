from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.auth import service
from app.auth.repository import UserRepository
from app.auth.schemas import User

oath2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/signin")


def get_user_repository(request: Request) -> UserRepository:
    return UserRepository(request.app.state.db)


async def get_current_user(
    token: str = Depends(oath2_scheme),
    repo: UserRepository = Depends(get_user_repository),
) -> User:
    payload = service.verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )

    found_result: dict = await repo.get(payload["email"])

    if not found_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return User(**found_result)
