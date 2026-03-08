from fastapi import Request

from app.auth.repository import UserRepository


def get_user_repository(request: Request) -> UserRepository:
    return UserRepository(request.app.state.db)
