from datetime import datetime
from typing import AsyncGenerator, Callable, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import EmailStr

from app.auth.dependencies import get_refresh_token_payload, get_user_repository
from app.auth.models import JwtTokenType, UserPayload
from app.auth.repository import AbstractUserRepository
from app.main import app


class FakeRepository(AbstractUserRepository):
    def __init__(self) -> None:
        self.user = {}

    async def create(self, user_data: dict) -> dict | None:
        return self.user

    async def get(self, email: EmailStr) -> dict | None:
        return self.user


@pytest.fixture
def test_refresh_payload() -> UserPayload:
    return UserPayload(
        email="test@example.com", exp=datetime.now(), type=JwtTokenType.REFRESH
    )


@pytest.fixture
def test_access_payload() -> UserPayload:
    return UserPayload(
        email="test@example.com", exp=datetime.now(), type=JwtTokenType.ACCESS
    )


@pytest.fixture
async def fake_repo() -> AsyncGenerator[FakeRepository, None]:
    repo = FakeRepository()

    app.dependency_overrides[get_user_repository] = lambda: repo

    yield repo

    app.dependency_overrides.pop(get_user_repository, None)


@pytest.fixture
def fake_refresh_token_payload(
    test_refresh_payload: UserPayload,
) -> Generator[UserPayload, None, None]:
    app.dependency_overrides[get_refresh_token_payload] = lambda: test_refresh_payload

    yield test_refresh_payload

    app.dependency_overrides.pop(get_refresh_token_payload, None)


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
def mock_verify_token(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[UserPayload | None], None]:
    def _mock(return_value: UserPayload | None) -> None:
        monkeypatch.setattr("app.auth.service.verify_token", lambda x: return_value)

    return _mock
