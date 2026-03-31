from datetime import datetime
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from pwdlib import PasswordHash
from pydantic import EmailStr
from pytest_mock import MockerFixture

from app.auth.dependencies import (
    get_current_user,
    get_refresh_token_data,
    get_refresh_token_repository,
    get_user_repository,
)
from app.auth.models import JwtTokenType, UserPayload
from app.auth.repositories import AbstractRefreshTokenRepository, AbstractUserRepository
from app.auth.schemas import User
from app.main import app

password_hash = PasswordHash.recommended()


class FakeUserRepository(AbstractUserRepository):
    def __init__(self) -> None:
        self.user = {}

    async def create(self, data: dict) -> User | None:
        return self._map_to_domain(self.user) if self.user else None

    async def get_by_email(self, email: EmailStr) -> User | None:
        return self._map_to_domain(self.user) if self.user else None

    async def get_by_id(self, id: str) -> User | None:
        return self._map_to_domain(self.user) if self.user else None

    def _map_to_domain(self, document: dict) -> User:
        return User(
            id=document["_id"],
            name=document["name"],
            email=document["email"],
            password_hash=document["password"],
        )


class FakeRefreshTokenRepository(AbstractRefreshTokenRepository):
    def __init__(self) -> None:
        self.token = {}

    def _hash_token(self, token: str) -> str:
        return "dummy"

    async def create(
        self, user_id: str, refresh_token: str, expired_at: datetime
    ) -> None: ...

    async def is_found_and_deleted(self, user_id: str, refresh_token: str) -> bool:
        return self.token is not None

    async def revoke_all(self, user_id: str) -> None: ...


@pytest.fixture
def test_refresh_token_payload() -> UserPayload:
    return UserPayload(
        sub="test_user_id_123", exp=datetime.now(), type=JwtTokenType.REFRESH
    )


@pytest.fixture
def test_access_token_payload() -> UserPayload:
    return UserPayload(
        sub="test_user_id_123", exp=datetime.now(), type=JwtTokenType.ACCESS
    )


@pytest.fixture
def user_signup_payload() -> dict:
    """Provides valid signup data."""
    return {
        "name": "test user",
        "email": "test@example.com",
        "password": "secure_password",
    }


@pytest.fixture
def db_user(user_signup_payload: dict) -> dict:
    """Provides a mock DB user based on the signup data."""
    return {
        "_id": "mock_id",
        "name": user_signup_payload["name"],
        "email": user_signup_payload["email"],
        "password": password_hash.hash(user_signup_payload["password"]),
    }


@pytest.fixture
def test_user(db_user: dict) -> User:
    return User(
        id=db_user["_id"],
        email=db_user["email"],
        name=db_user["name"],
        password_hash=db_user["password"],
    )


@pytest.fixture
async def fake_user_repo() -> AsyncGenerator[FakeUserRepository, None]:
    repo = FakeUserRepository()

    app.dependency_overrides[get_user_repository] = lambda: repo

    yield repo

    app.dependency_overrides.pop(get_user_repository, None)


@pytest.fixture
async def fake_refresh_token_repo() -> AsyncGenerator[FakeRefreshTokenRepository, None]:
    repo = FakeRefreshTokenRepository()

    app.dependency_overrides[get_refresh_token_repository] = lambda: repo

    yield repo

    app.dependency_overrides.pop(get_refresh_token_repository, None)


@pytest.fixture
def fake_refresh_token_data_dependency(
    test_refresh_token_payload: UserPayload,
) -> Generator[UserPayload, None, None]:
    data: tuple = (test_refresh_token_payload, "random_token")
    app.dependency_overrides[get_refresh_token_data] = lambda: data

    yield data

    app.dependency_overrides.pop(get_refresh_token_data, None)


@pytest.fixture
def fake_current_user_dependency(test_user: User) -> Generator[User, None, None]:
    app.dependency_overrides[get_current_user] = lambda: test_user

    yield test_user

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with app.router.lifespan_context(app) as _:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client


@pytest.fixture
def mock_jwt_decode(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("app.auth.service.jwt.decode")
