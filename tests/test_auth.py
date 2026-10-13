import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.infrastructure.db.models import User, Session
from app.modules.auth.password import PasswordService


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, db_session):
    payload = {
        "username": "daniel",
        "email": "daniel@example.com",
        "password": "password123",
    }

    response = await client.post(
        "/api/auth/register",
        json=payload,
    )


    assert response.status_code == 201

    data = response.json()

    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]

    assert "public_id" in data
    assert "password" not in data
    assert "password_hash" not in data

    result = await db_session.execute(
        select(User).where(User.email == payload["email"])
    )

    user = result.scalar_one()

    assert user.username == payload["username"]
    assert user.password_hash != payload["password"]

    assert PasswordService.verify_password(
        payload["password"],
        user.password_hash,
    )


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "username": "daniel",
        "email": "daniel@example.com",
        "password": "password123",
    }

    response = await client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code == 201

    response = await client.post(
        "/api/auth/register",
        json={
            "username": "another",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    payload = {
        "username": "daniel",
        "email": "daniel@example.com",
        "password": "password123",
    }

    response = await client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code == 201

    response = await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "another@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_password(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "123",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "invalid-email",
            "password": "password123",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    payload = {
        "username": "daniel",
        "email": "daniel@example.com",
        "password": "password123",
    }

    register_response = await client.post(
        "/api/auth/register",
        json=payload,
    )

    assert register_response.status_code == 201

    # register уже установил cookies.
    # Очищаем их, чтобы проверить именно login.
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": payload["username"],
            "password": payload["password"],
        },
    )

    assert response.status_code == 204

    assert "access_token" in client.cookies
    assert "refresh_token" in client.cookies


@pytest.mark.asyncio
async def test_login_invalid_username(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "not_exists",
            "password": "password123",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "daniel",
            "password": "wrong_password",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_creates_session(client: AsyncClient, db_session):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    result = await db_session.execute(
        select(Session)
    )

    sessions = result.scalars().all()

    assert len(sessions) == 1
    assert sessions[0].deleted_at is None
    assert sessions[0].refresh_token_hash


@pytest.mark.asyncio
async def test_get_sessions(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    response = await client.get(
        "/api/auth/sessions"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1

    session = data[0]

    assert "public_id" in session
    assert "ip_address" in session
    assert "user_agent" in session
    assert "is_current" in session
    assert session["is_current"] is True


@pytest.mark.asyncio
async def test_get_sessions_without_auth(client: AsyncClient):
    response = await client.get(
        "/api/auth/sessions"
    )

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    assert "access_token" in client.cookies
    assert "refresh_token" in client.cookies

    old_access_token = client.cookies.get("access_token")

    response = await client.post("/api/auth/refresh")

    assert response.status_code == 204

    new_access_token = client.cookies.get("access_token")

    assert new_access_token
    assert new_access_token != old_access_token


@pytest.mark.asyncio
async def test_refresh_without_token(client: AsyncClient):
    response = await client.post(
        "/api/auth/refresh"
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, db_session):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/auth/logout"
    )

    assert response.status_code == 204

    assert "access_token" not in client.cookies
    assert "refresh_token" not in client.cookies

    result = await db_session.execute(
        select(Session)
    )

    session = result.scalar_one()

    assert session.deleted_at is not None


@pytest.mark.asyncio
async def test_logout_without_auth(client: AsyncClient):
    response = await client.post(
        "/api/auth/logout"
    )

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_password_change_success(client: AsyncClient, db_session):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/auth/password-change",
        json={
            "old_password": "password123",
            "new_password": "new_password123",
        },
    )

    assert response.status_code == 204

    result = await db_session.execute(
        select(User).where(User.username == "daniel")
    )

    user = result.scalar_one()

    assert PasswordService.verify_password(
        "new_password123",
        user.password_hash,
    )


@pytest.mark.asyncio
async def test_password_change_wrong_old_password(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/auth/password-change",
        json={
            "old_password": "wrong_password",
            "new_password": "new_password123",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_password_change_same_password(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/auth/password-change",
        json={
            "old_password": "password123",
            "new_password": "password123",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_change_email_success(client: AsyncClient, db_session):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    response = await client.patch(
        "/api/auth/email/change",
        json={
            "email": "new@example.com",
        },
    )

    assert response.status_code == 204

    result = await db_session.execute(
        select(User).where(User.username == "daniel")
    )

    user = result.scalar_one()

    assert user.email == "new@example.com"
    assert user.email_verified_at is None


@pytest.mark.asyncio
async def test_change_email_same_email(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    response = await client.patch(
        "/api/auth/email/change",
        json={
            "email": "daniel@example.com",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_change_email_duplicate(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/register",
        json={
            "username": "another",
            "email": "another@example.com",
            "password": "password123",
        },
    )

    response = await client.patch(
        "/api/auth/email/change",
        json={
            "email": "daniel@example.com",
        },
    )

    assert response.status_code == 409