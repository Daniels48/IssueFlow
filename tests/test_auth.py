import pytest
from httpx import AsyncClient

from app.infrastructure.db.models import User
from app.modules.auth.password import PasswordService

from sqlalchemy import select


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "daniel"
    assert data["email"] == "daniel@example.com"
    assert "public_id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "username": "daniel",
        "email": "daniel@example.com",
        "password": "password123",
    }

    await client.post("/api/auth/register", json=payload)

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

    await client.post("/api/auth/register", json=payload)

    response = await client.post(
        "api/auth/register",
        json={
            "username": "daniel",
            "email": "another@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_password_is_hashed(client: AsyncClient,db_session):
    payload = {
        "username": "daniel",
        "email": "daniel@example.com",
        "password": "password123",
    }

    await client.post("/api/auth/register", json=payload)

    result = await db_session.execute(
        select(User).where(User.email == payload["email"])
    )

    user = result.scalar_one()

    assert user.password_hash != payload["password"]

    assert PasswordService.verify_password(
        payload["password"],
        user.password_hash,
    )