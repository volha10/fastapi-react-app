from dataclasses import asdict
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import status
from httpx import AsyncClient
from pwdlib import PasswordHash
from pytest_mock import MockerFixture

from app.auth.models import UserPayload
from app.auth.schemas import User
from app.core.config import settings
from tests.conftest import FakeRefreshTokenRepository, FakeUserRepository

USERS_PATH = "api/v1/users"
USER_DATA = {"username": "test@example.com", "password": "test_password123"}

password_hash = PasswordHash.recommended()


async def test_signup_status_code_on_success(
    async_client: AsyncClient,
    fake_user_repo: FakeUserRepository,
    user_signup_payload: dict,
    db_user: dict,
) -> None:
    fake_user_repo.user = db_user

    response = await async_client.post(f"{USERS_PATH}/signup", json=user_signup_payload)

    assert response.status_code == status.HTTP_200_OK


async def test_signup_response_data_on_success(
    async_client: AsyncClient,
    fake_user_repo: FakeUserRepository,
    user_signup_payload: dict,
    db_user: dict,
) -> None:
    fake_user_repo.user = db_user

    response = await async_client.post(f"{USERS_PATH}/signup", json=user_signup_payload)

    assert response.json() == {
        "email": db_user["email"],
        "id": db_user["_id"],
        "name": db_user["name"],
    }


async def test_signup_status_code_on_conflict(
    async_client: AsyncClient,
    fake_user_repo: FakeUserRepository,
    user_signup_payload: dict,
    db_user: dict,
) -> None:
    fake_user_repo.user = None

    response = await async_client.post(f"{USERS_PATH}/signup", json=user_signup_payload)

    assert response.status_code == status.HTTP_409_CONFLICT


async def test_signup_response_data_on_conflict(
    async_client: AsyncClient,
    fake_user_repo: FakeUserRepository,
    user_signup_payload: dict,
    db_user: dict,
) -> None:
    fake_user_repo.user = None

    response = await async_client.post(f"{USERS_PATH}/signup", json=user_signup_payload)

    assert response.json() == {"detail": "The user with this email already exists"}


async def test_signin_status_code_on_success(
    async_client: AsyncClient, fake_user_repo: FakeUserRepository, db_user: dict
) -> None:
    """Verifies 200 OK for valid credentials."""

    raw_password = "secure_password"
    fake_user_repo.user = db_user

    response = await async_client.post(
        f"{USERS_PATH}/signin",
        data={"username": "test@example.com", "password": raw_password},
    )

    assert response.status_code == status.HTTP_200_OK


async def test_signin_response_data_on_success(
    async_client: AsyncClient, fake_user_repo: FakeUserRepository, db_user: dict
) -> None:
    """Verifies the token structure in the response body."""
    raw_password = "secure_password"
    fake_user_repo.user = db_user

    response = await async_client.post(
        f"{USERS_PATH}/signin",
        data={"username": "test@example.com", "password": raw_password},
    )
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


async def test_signin_error_detail_on_invalid_credentials(
    async_client: AsyncClient, fake_user_repo: FakeUserRepository
) -> None:
    """Verifies the specific exception detail message."""
    fake_user_repo.user = None

    response = await async_client.post(
        f"{USERS_PATH}/signin",
        data={"username": "notfound@example.com", "password": "any_password"},
    )

    assert response.json() == {"detail": "Incorrect email or password"}


async def test_refresh_status_code_on_success(
    async_client: AsyncClient,
    test_refresh_token_payload: UserPayload,
    fake_refresh_token_repo: FakeRefreshTokenRepository,
    mock_jwt_decode: MagicMock,
) -> None:
    mock_jwt_decode.return_value = asdict(test_refresh_token_payload)

    valid_refresh_token = "some-valid-token"
    fake_refresh_token_repo.token = {
        "user_id": test_refresh_token_payload.sub,
        "token_hash": "some-valid-token-hash",
        "exprired_at": test_refresh_token_payload.exp,
    }

    response = await async_client.post(
        f"/{USERS_PATH}/refresh", headers={"X-Refresh-Token": valid_refresh_token}
    )

    assert response.status_code == status.HTTP_200_OK


async def test_refresh_response_data_on_success(
    async_client: AsyncClient,
    test_refresh_token_payload: UserPayload,
    fake_refresh_token_repo: FakeRefreshTokenRepository,
    mock_jwt_decode: MagicMock,
) -> None:
    mock_jwt_decode.return_value = asdict(test_refresh_token_payload)

    fake_refresh_token_repo.token = {
        "user_id": test_refresh_token_payload.sub,
        "token_hash": "some-valid-token-hash",
        "exprired_at": test_refresh_token_payload.exp,
    }
    response = await async_client.post(
        url=f"{USERS_PATH}/refresh",
        headers={"X-Refresh-Token": "some-valid-token-hash"},
    )

    response_data = response.json()
    assert response_data["token_type"] == "Bearer"
    assert "access_token" in response_data
    assert "refresh_token" in response_data


@pytest.mark.parametrize(
    "jwt_error", [jwt.ExpiredSignatureError, jwt.InvalidSignatureError]
)
async def test_refresh_status_code_on_invalid_token(
    jwt_error: type[Exception],
    async_client: AsyncClient,
    mock_jwt_decode: MagicMock,
) -> None:
    mock_jwt_decode.side_effect = jwt_error

    response = await async_client.post(
        f"{USERS_PATH}/refresh", headers={"X-Refresh-Token": "some-dummy-token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "jwt_error", [jwt.ExpiredSignatureError, jwt.InvalidSignatureError]
)
async def test_refresh_response_data_on_invalid_token(
    jwt_error: type[Exception],
    async_client: AsyncClient,
    mock_jwt_decode: MagicMock,
    test_access_token_payload: UserPayload,
) -> None:
    mock_jwt_decode.side_effect = jwt_error

    response = await async_client.post(
        f"{USERS_PATH}/refresh", headers={"X-Refresh-Token": "some-dummy-token"}
    )

    assert response.json()["detail"] == "Token is invalid or expired"


async def test_refresh_status_code_on_wrong_token_type(
    async_client: AsyncClient,
    mock_jwt_decode: MagicMock,
    test_access_token_payload: UserPayload,
) -> None:
    mock_jwt_decode.return_value = asdict(test_access_token_payload)

    response = await async_client.post(
        f"{USERS_PATH}/refresh", headers={"X-Refresh-Token": "some-dummy-token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_refresh_response_data_on_wrong_token_type(
    async_client: AsyncClient,
    mock_jwt_decode: MagicMock,
    test_access_token_payload: UserPayload,
) -> None:
    mock_jwt_decode.return_value = asdict(test_access_token_payload)

    response = await async_client.post(
        f"{USERS_PATH}/refresh", headers={"X-Refresh-Token": "some-dummy-token"}
    )

    assert response.json()["detail"] == "Token is invalid or expired"


async def test_refresh_call_jwt_decode_with_correct_arguments(
    async_client: AsyncClient,
    mock_jwt_decode: MagicMock,
    test_refresh_token_payload: UserPayload,
) -> None:
    token_str = "some-real-looking-token"
    mock_jwt_decode.return_value = asdict(test_refresh_token_payload)

    await async_client.post(
        f"/{USERS_PATH}/refresh", headers={"X-Refresh-Token": token_str}
    )

    mock_jwt_decode.assert_called_once_with(
        token_str, key=settings.APP_JWT_SECRET, algorithms=[settings.APP_JWT_ALG]
    )


async def test_refresh_status_code_on_token_reuse_error(
    async_client: AsyncClient,
    fake_refresh_token_data_dependency: tuple[UserPayload, str],
) -> None:
    """Verify that valid but missing in DB refresh token returns 401."""

    response = await async_client.post(
        f"{USERS_PATH}/refresh", headers={"X-Refresh-Token": "some-dummy-token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_refresh_response_data_on_token_reuse_error(
    async_client: AsyncClient,
    fake_refresh_token_data_dependency: tuple[UserPayload, str],
) -> None:
    """Verify that valid but missing in DB refresh token contains the correct error detail."""

    response = await async_client.post(
        f"{USERS_PATH}/refresh", headers={"X-Refresh-Token": "some-dummy-token"}
    )

    assert response.json()["detail"] == "Security alert: Token reuse detected"


async def test_me_status_code_on_success(
    async_client: AsyncClient,
    fake_current_user_dependency: User,
) -> None:
    """Verify that a request with valid credentials returns 200."""

    response = await async_client.get(f"/{USERS_PATH}/me")

    assert response.status_code == status.HTTP_200_OK


async def test_me_response_data_on_success(
    async_client: AsyncClient,
    fake_current_user_dependency: User,
) -> None:
    response = await async_client.get(
        url=f"{USERS_PATH}/me",
    )
    """Verify that a request with valid credentials returns correct data."""

    response_data = response.json()

    assert response_data == {
        "id": "mock_id",
        "name": "test user",
        "email": "test@example.com",
    }
    assert "password" not in response_data
    assert "password_hash" not in response_data


async def test_me_unauthorized_status_code(
    async_client: AsyncClient,
) -> None:
    """Verify that a request without credentials returns 401."""

    response = await async_client.get(f"/{USERS_PATH}/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_me_unauthorized_response_data(
    async_client: AsyncClient,
) -> None:
    """Verify that a request without credentials returns correct error detail."""

    response = await async_client.get(f"/{USERS_PATH}/me")

    response_data = response.json()

    assert response_data == {"detail": "Not authenticated"}


async def test_logout_status_code_if_valid_token_was_found_in_db(
    async_client: AsyncClient,
    fake_refresh_token_data_dependency: tuple[UserPayload, str],
    fake_refresh_token_repo: FakeRefreshTokenRepository,
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(
        fake_refresh_token_repo, "is_found_and_deleted", return_value=True
    )

    response = await async_client.post(
        f"{USERS_PATH}/logout", headers={"X-Refresh-Token": "dummy"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_logout_status_code_if_valid_token_was_not_found_in_db(
    async_client: AsyncClient,
    fake_refresh_token_data_dependency: tuple[UserPayload, str],
    fake_refresh_token_repo: FakeRefreshTokenRepository,
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(
        fake_refresh_token_repo, "is_found_and_deleted", return_value=False
    )

    response = await async_client.post(
        f"{USERS_PATH}/logout", headers={"X-Refresh-Token": "dummy"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_logout_status_code_if_invalid_token(async_client: AsyncClient) -> None:
    response = await async_client.post(
        f"{USERS_PATH}/logout", headers={"X-Refresh-Token": "dummy"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_logout_response_data_if_invalid_token(async_client: AsyncClient) -> None:
    response = await async_client.post(
        f"{USERS_PATH}/logout", headers={"X-Refresh-Token": "dummy"}
    )
    response_data = response.json()

    assert response_data == {"detail": "Token is invalid or expired"}
