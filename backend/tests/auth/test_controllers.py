from httpx import AsyncClient

PREFIX = "api/v1/users"
USER_DATA = {"username": "test@example.com", "password": "test_password123"}

async def test_signup_status_code_on_success(async_client: AsyncClient, fake_repo, user_signup_payload: dict, db_user: dict):
    fake_repo.user = db_user

    response = await async_client.post(f"{PREFIX}/signup", json=user_signup_payload)

    assert response.status_code == 200


async def test_signup_response_data_on_success(async_client: AsyncClient, fake_repo, user_signup_payload: dict, db_user: dict):
    fake_repo.user = db_user

    response = await async_client.post(f"{PREFIX}/signup", json=user_signup_payload)

    assert response.json() == {'email': db_user["email"], 'id': db_user["_id"], 'name': db_user["name"]}



async def test_signup_status_code_on_conflict(async_client: AsyncClient, fake_repo, user_signup_payload: dict, db_user: dict):
    fake_repo.user = None

    response = await async_client.post(f"{PREFIX}/signup", json=user_signup_payload)

    assert response.status_code == 409


async def test_signup_response_data_on_conflict(async_client: AsyncClient, fake_repo, user_signup_payload: dict, db_user: dict):
    fake_repo.user = None

    response = await async_client.post(f"{PREFIX}/signup", json=user_signup_payload)

    assert response.json() == {'detail': 'The user with this email already exists'}

