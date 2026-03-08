from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import EmailStr

from app.auth.dependencies import get_user_repository
from app.main import app


class FakeRepository:
    def __init__(self) -> None:
        self.user = {}

    async def create(self, _: dict) -> dict | None:
        return self.user

    async def get(self, _: EmailStr) -> dict | None:
        return self.user


@pytest.fixture
async def fake_repo() -> AsyncGenerator[FakeRepository, None]:
    repo = FakeRepository()

    app.dependency_overrides[get_user_repository] = lambda: repo

    yield repo

    app.dependency_overrides.clear()


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
