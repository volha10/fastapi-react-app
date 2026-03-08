from fastapi import status
from httpx import AsyncClient
from pwdlib import PasswordHash

from tests.conftest import FakeRepository

PREFIX = "api/v1/users"
USER_DATA = {"username": "test@example.com", "password": "test_password123"}

password_hash = PasswordHash.recommended()

async def test_signup_status_code_on_success(async_client: AsyncClient, fake_repo: FakeRepository, user_signup_payload: dict, db_user: dict):
    fake_repo.user = db_user

    response = await async_client.post(f"{PREFIX}/signup", json=user_signup_payload)

    assert response.status_code == status.HTTP_200_OK


async def test_signup_response_data_on_success(async_client: AsyncClient, fake_repo: FakeRepository, user_signup_payload: dict, db_user: dict):
    fake_repo.user = db_user

    response = await async_client.post(f"{PREFIX}/signup", json=user_signup_payload)

    assert response.json() == {'email': db_user["email"], 'id': db_user["_id"], 'name': db_user["name"]}



async def test_signup_status_code_on_conflict(async_client: AsyncClient, fake_repo: FakeRepository, user_signup_payload: dict, db_user: dict):
    fake_repo.user = None

    response = await async_client.post(f"{PREFIX}/signup", json=user_signup_payload)

    assert response.status_code == status.HTTP_409_CONFLICT


async def test_signup_response_data_on_conflict(async_client: AsyncClient, fake_repo: FakeRepository, user_signup_payload: dict, db_user: dict):
    fake_repo.user = None

    response = await async_client.post(f"{PREFIX}/signup", json=user_signup_payload)

    assert response.json() == {'detail': 'The user with this email already exists'}


async def test_signin_status_code_on_success(async_client: AsyncClient, fake_repo: FakeRepository):
    """Verifies 200 OK for valid credentials."""
    raw_password = "secure_password"
    fake_repo.user = {
        "email": "test@example.com",
        "password": password_hash.hash(raw_password)
    }

    response = await async_client.post(
        f"{PREFIX}/signin",
        data={"username": "test@example.com", "password": raw_password}
    )

    assert response.status_code == status.HTTP_200_OK


async def test_signin_response_data_on_success(async_client: AsyncClient, fake_repo: FakeRepository):
    """Verifies the token structure in the response body."""
    raw_password = "secure_password"
    fake_repo.user = {
        "email": "test@example.com",
        "password": password_hash.hash(raw_password)
    }

    response = await async_client.post(
        f"{PREFIX}/signin",
        data={"username": "test@example.com", "password": raw_password}
    )
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


async def test_signin_error_detail_on_invalid_credentials(async_client: AsyncClient, fake_repo: FakeRepository):
    """Verifies the specific exception detail message."""
    fake_repo.user = None

    response = await async_client.post(
        f"{PREFIX}/signin",
        data={"username": "notfound@example.com", "password": "any_password"}
    )

    assert response.json() == {"detail": "Incorrect email or password"}
