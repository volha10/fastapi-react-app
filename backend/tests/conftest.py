from datetime import datetime
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import EmailStr
from pytest_mock import MockerFixture

from app.auth.dependencies import get_refresh_token_data, get_user_repository
from app.auth.models import JwtTokenType, UserPayload
from app.auth.repositories import AbstractUserRepository
from app.auth.schemas import User
from app.main import app


class FakeUserRepository(AbstractUserRepository):
    def __init__(self) -> None:
        self.user = {}

    async def create(self, user_data: dict) -> dict | None:
        return self.user

    async def get(self, email: EmailStr) -> User | None:
        return self.user


@pytest.fixture
def test_refresh_payload() -> UserPayload:
    return UserPayload(
        sub="test_user_id_123", exp=datetime.now(), type=JwtTokenType.REFRESH
    )


@pytest.fixture
def test_access_payload() -> UserPayload:
    return UserPayload(
        sub="test_user_id_123", exp=datetime.now(), type=JwtTokenType.ACCESS
    )


@pytest.fixture
async def fake_repo() -> AsyncGenerator[FakeUserRepository, None]:
    repo = FakeUserRepository()

    app.dependency_overrides[get_user_repository] = lambda: repo

    yield repo

    app.dependency_overrides.pop(get_user_repository, None)


@pytest.fixture
def fake_refresh_token_payload(
    test_refresh_payload: UserPayload,
) -> Generator[UserPayload, None, None]:
    data: tuple = (test_refresh_payload, "random_token") 
    app.dependency_overrides[get_refresh_token_data] = lambda: data

    yield data

    app.dependency_overrides.pop(get_refresh_token_data, None)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with app.router.lifespan_context(app) as _:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client


@pytest.fixture
def user_signup_payload() -> dict:
    """Provides valid signup data."""
    return {
        "name": "test user",
        "email": "test@example.com",
        "password": "test_password123",
    }


@pytest.fixture
def db_user(user_signup_payload: dict) -> dict:
    """Provides a mock DB user based on the signup data."""
    return {
        "name": user_signup_payload["name"],
        "email": user_signup_payload["email"],
        "_id": "mock_id",
    }


@pytest.fixture
def mock_jwt_decode(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("app.auth.service.jwt.decode")
