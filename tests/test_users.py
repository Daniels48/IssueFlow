import pytest
from httpx import AsyncClient

from tests.test_members import register_user, create_project


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    response = await client.get("/api/users/me")

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "owner"
    assert data["email"] == "owner@example.com"
    assert "public_id" in data
    assert "is_active" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_search_users_success(client: AsyncClient):
    owner = await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    other = await register_user(
        client,
        "member",
        "member@example.com",
    )

    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code in (200, 204)

    project = await create_project(client)

    response = await client.get(
        "/api/users/search",
        params={
            "query": "mem",
            "project_id": project["public_id"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["username"] == "member"
    assert data[0]["public_id"] == other["public_id"]


@pytest.mark.asyncio
async def test_search_users_excludes_current_user(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    member = await register_user(
        client,
        "member",
        "member@example.com",
    )

    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code in (200, 204)

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    assert response.status_code == 201

    response = await client.get(
        "/api/users/search",
        params={
            "query": "",
            "project_id": project["public_id"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    usernames = {item["username"] for item in data}

    assert "owner" not in usernames
    assert "member" not in usernames

@pytest.mark.asyncio
async def test_search_users_project_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    response = await client.get(
        "/api/users/search",
        params={
            "query": "test",
            "project_id": "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code == 404
    assert response.json() == []


@pytest.mark.asyncio
async def test_search_users_without_auth(client: AsyncClient):
    response = await client.get(
        "/api/users/search",
        params={
            "query": "test",
            "project_id": "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_search_users_without_project_membership(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    other = await register_user(
        client,
        "other",
        "other@example.com",
    )

    project = await create_project(client)

    response = await client.get(
        "/api/users/search",
        params={
            "query": "other",
            "project_id": project["public_id"],
        },
    )

    assert response.status_code == 403