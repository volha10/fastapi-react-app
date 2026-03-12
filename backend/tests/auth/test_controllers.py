from typing import Callable

from fastapi import status
from httpx import AsyncClient
from pwdlib import PasswordHash

from app.auth.models import UserPayload
from tests.conftest import FakeRepository

USERS_PATH = "api/v1/users"
USER_DATA = {"username": "test@example.com", "password": "test_password123"}

password_hash = PasswordHash.recommended()


async def test_signup_status_code_on_success(
    async_client: AsyncClient,
    fake_repo: FakeRepository,
    user_signup_payload: dict,
    db_user: dict,
) -> None:
    fake_repo.user = db_user

    response = await async_client.post(f"{USERS_PATH}/signup", json=user_signup_payload)

    assert response.status_code == status.HTTP_200_OK


async def test_signup_response_data_on_success(
    async_client: AsyncClient,
    fake_repo: FakeRepository,
    user_signup_payload: dict,
    db_user: dict,
) -> None:
    fake_repo.user = db_user

    response = await async_client.post(f"{USERS_PATH}/signup", json=user_signup_payload)

    assert response.json() == {
        "email": db_user["email"],
        "id": db_user["_id"],
        "name": db_user["name"],
    }


async def test_signup_status_code_on_conflict(
    async_client: AsyncClient,
    fake_repo: FakeRepository,
    user_signup_payload: dict,
    db_user: dict,
) -> None:
    fake_repo.user = None

    response = await async_client.post(f"{USERS_PATH}/signup", json=user_signup_payload)

    assert response.status_code == status.HTTP_409_CONFLICT


async def test_signup_response_data_on_conflict(
    async_client: AsyncClient,
    fake_repo: FakeRepository,
    user_signup_payload: dict,
    db_user: dict,
) -> None:
    fake_repo.user = None

    response = await async_client.post(f"{USERS_PATH}/signup", json=user_signup_payload)

    assert response.json() == {"detail": "The user with this email already exists"}


async def test_signin_status_code_on_success(
    async_client: AsyncClient, fake_repo: FakeRepository
) -> None:
    """Verifies 200 OK for valid credentials."""
    raw_password = "secure_password"
    fake_repo.user = {
        "email": "test@example.com",
        "password": password_hash.hash(raw_password),
    }

    response = await async_client.post(
        f"{USERS_PATH}/signin",
        data={"username": "test@example.com", "password": raw_password},
    )

    assert response.status_code == status.HTTP_200_OK


async def test_signin_response_data_on_success(
    async_client: AsyncClient, fake_repo: FakeRepository
) -> None:
    """Verifies the token structure in the response body."""
    raw_password = "secure_password"
    fake_repo.user = {
        "email": "test@example.com",
        "password": password_hash.hash(raw_password),
    }

    response = await async_client.post(
        f"{USERS_PATH}/signin",
        data={"username": "test@example.com", "password": raw_password},
    )
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


async def test_signin_error_detail_on_invalid_credentials(
    async_client: AsyncClient, fake_repo: FakeRepository
) -> None:
    """Verifies the specific exception detail message."""
    fake_repo.user = None

    response = await async_client.post(
        f"{USERS_PATH}/signin",
        data={"username": "notfound@example.com", "password": "any_password"},
    )

    assert response.json() == {"detail": "Incorrect email or password"}


async def test_refresh_status_code_on_success(
    async_client: AsyncClient, fake_refresh_token_payload: UserPayload
) -> None:
    response = await async_client.post(url=f"{USERS_PATH}/refresh")

    assert response.status_code == status.HTTP_200_OK


async def test_refresh_response_data_on_success(
    async_client: AsyncClient, fake_refresh_token_payload: UserPayload
) -> None:
    response = await async_client.post(url=f"{USERS_PATH}/refresh")

    response_data = response.json()
    assert response_data["token_type"] == "Bearer"
    assert "access_token" in response_data
    assert "refresh_token" in response_data


async def test_refresh_status_code_on_invalid_token(
    async_client: AsyncClient, mock_verify_token: Callable[[UserPayload | None], None]
) -> None:
    mock_verify_token(None)

    response = await async_client.post(
        f"{USERS_PATH}/refresh", headers={"X-Refresh-Token": "some-dummy-token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_refresh_response_data_on_invalid_token(
    async_client: AsyncClient, mock_verify_token: Callable[[UserPayload | None], None]
) -> None:
    mock_verify_token(None)

    response = await async_client.post(
        f"{USERS_PATH}/refresh", headers={"X-Refresh-Token": "some-dummy-token"}
    )

    assert response.json()["detail"] == "Token is invalid or expired"


async def test_refresh_status_code_on_wrong_token_type(
    async_client: AsyncClient,
    mock_verify_token: Callable[[UserPayload | None], None],
    test_access_payload: UserPayload,
) -> None:
    mock_verify_token(test_access_payload)

    response = await async_client.post(
        f"{USERS_PATH}/refresh", headers={"X-Refresh-Token": "some-dummy-token"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_refresh_response_data_on_wrong_token_type(
    async_client: AsyncClient,
    mock_verify_token: Callable[[UserPayload | None], None],
    test_access_payload: UserPayload,
) -> None:
    mock_verify_token(test_access_payload)

    response = await async_client.post(
        f"{USERS_PATH}/refresh", headers={"X-Refresh-Token": "some-dummy-token"}
    )

    assert response.json()["detail"] == "Invalid token type"
