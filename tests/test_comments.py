import pytest
from httpx import AsyncClient

from tests.test_members import register_user, create_project


@pytest.mark.asyncio
async def test_create_comment_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    assert response.status_code == 201

    issue = response.json()

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments",
        json={
            "content": "Test comment",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["content"] == "Test comment"
    assert data["author"]["username"] == "owner"
    assert data["parent_comment_public_id"] is None
    assert data["deleted_at"] is None
    assert data["replies_count"] == 0


@pytest.mark.asyncio
async def test_get_comments_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    for content in ["Comment 1", "Comment 2"]:
        response = await client.post(
            f"/api/projects/{project['public_id']}/issues/"
            f"{issue['public_id']}/comments",
            json={
                "content": content,
            },
        )

        assert response.status_code == 201

    response = await client.get(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert data["has_more"] is False

    contents = {
        item["content"]
        for item in data["items"]
    }

    assert contents == {"Comment 1", "Comment 2"}


@pytest.mark.asyncio
async def test_create_comment_without_auth(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    client.cookies.clear()

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments",
        json={
            "content": "Test comment",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_comments_without_auth(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    client.cookies.clear()

    response = await client.get(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments"
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_comment_issue_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/"
        "00000000-0000-0000-0000-000000000000/comments",
        json={
            "content": "Test comment",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_comment_without_membership(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    await register_user(
        client,
        "member",
        "member@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "member",
            "password": "password123",
        },
    )

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments",
        json={
            "content": "Test comment",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_comment_empty_content(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments",
        json={
            "content": "",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_comment_too_long(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments",
        json={
            "content": "x" * 5001,
        },
    )

    assert response.status_code == 422


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
async def test_create_reply_parent_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments",
        json={
            "content": "Reply",
            "parent_comment_public_id":
                "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_comment_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments",
        json={
            "content": "Old content",
        },
    )

    comment = response.json()

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments/{comment['public_id']}",
        json={
            "content": "New content",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "New content"


@pytest.mark.asyncio
async def test_member_cannot_update_comment(client: AsyncClient):
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

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments",
        json={
            "content": "Owner comment",
        },
    )

    comment = response.json()

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "member",
            "password": "password123",
        },
    )

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments/{comment['public_id']}",
        json={
            "content": "Hacked",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments",
        json={
            "content": "Test comment",
        },
    )

    comment = response.json()

    response = await client.delete(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments/{comment['public_id']}"
    )

    assert response.status_code == 204

    response = await client.get(
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/comments"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0


@pytest.mark.asyncio
async def test_delete_comment_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    project = await create_project(client)

    response = await client.delete(
        f"/api/projects/{project['public_id']}/issues/"
        f"00000000-0000-0000-0000-000000000000/comments/"
        "00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404