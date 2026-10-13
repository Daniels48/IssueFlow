import pytest
from httpx import AsyncClient

from app.infrastructure.db.models import ProjectMember
from app.modules.project_members.project_role import ProjectRole


async def register_user(client: AsyncClient,username: str,email: str,password: str = "password123"):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    return response.json()


async def create_project( client: AsyncClient,name: str = "Test project"):
    response = await client.post(
        "/api/projects",
        json={
            "name": name,
            "description": "Test description",
        },
    )

    assert response.status_code == 201

    return response.json()


@pytest.mark.asyncio
async def test_add_member_success(client: AsyncClient):
    owner = await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    await client.post("/api/auth/logout")

    member = await register_user(
        client,
        "member",
        "member@example.com",
    )

    # Сейчас cookies принадлежат member.
    # Переключаемся на owner.
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Теперь проект создаётся owner'ом
    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user"]["public_id"] == member["public_id"]
    assert data["user"]["username"] == "member"
    assert data["role"] == ProjectRole.MEMBER


@pytest.mark.asyncio
async def test_get_members_success(client: AsyncClient):
    # Создаём owner
    owner = await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    # Создаём member
    await client.post("/api/auth/logout")

    member = await register_user(
        client,
        "member",
        "member@example.com",
    )

    # Переключаемся обратно на owner
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Теперь проект действительно создаёт owner
    project = await create_project(client)

    # Owner добавляет member
    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    assert response.status_code == 201

    # Получаем участников
    response = await client.get(
        f"/api/projects/{project['public_id']}/members"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    usernames = {
        item["user"]["username"]
        for item in data
    }

    assert usernames == {"owner", "member"}


@pytest.mark.asyncio
async def test_add_member_without_auth(client: AsyncClient):
    response = await client.post(
        "/api/projects/00000000-0000-0000-0000-000000000000/members",
        json={
            "user_public_id": "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_members_without_auth(client: AsyncClient):
    response = await client.get(
        "/api/projects/00000000-0000-0000-0000-000000000000/members"
    )

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_add_member_project_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    response = await client.post(
        "/api/projects/00000000-0000-0000-0000-000000000000/members",
        json={
            "user_public_id": "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_members_project_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    response = await client.get(
        "/api/projects/00000000-0000-0000-0000-000000000000/members"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_member_user_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_duplicate_member(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    await client.post("/api/auth/logout")

    member = await register_user(
        client,
        "member",
        "member@example.com",
    )

    # Переключаемся на owner
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Теперь проект действительно принадлежит owner
    project = await create_project(client)

    # Первый раз добавляем member
    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    assert response.status_code == 201

    # Второй раз добавляем того же member
    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_member_cannot_add_member(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    await client.post("/api/auth/logout")

    member = await register_user(
        client,
        "member",
        "member@example.com",
    )

    await client.post("/api/auth/logout")

    another = await register_user(
        client,
        "another",
        "another@example.com",
    )

    # Переходим под owner
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Теперь проект создаёт owner
    project = await create_project(client)

    # Owner добавляет member
    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    assert response.status_code == 201

    # Переходим под member
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "member",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Member пытается добавить another
    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": another["public_id"],
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_member_can_get_members(client: AsyncClient):
    # Создаём owner
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    # Создаём member
    await client.post("/api/auth/logout")

    member = await register_user(
        client,
        "member",
        "member@example.com",
    )

    # Переходим под owner
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Проект создаёт owner
    project = await create_project(client)

    # Owner добавляет member
    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    assert response.status_code == 201

    # Переходим под member
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "member",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Member получает список участников
    response = await client.get(
        f"/api/projects/{project['public_id']}/members"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    usernames = {
        item["user"]["username"]
        for item in data
    }

    assert usernames == {"owner", "member"}


@pytest.mark.asyncio
async def test_update_member_role_success(client: AsyncClient):
    # Регистрируем owner
    owner = await register_user(client,"owner","owner@example.com")

    # Регистрируем member
    member = await register_user(client,"member","member@example.com",)

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
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    assert response.status_code == 201

    response = await client.patch(
        f"/api/projects/{project['public_id']}/members/{member['public_id']}",
        json={
            "role": ProjectRole.ADMIN,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user"]["public_id"] == member["public_id"]
    assert data["role"] == ProjectRole.ADMIN


@pytest.mark.asyncio
async def test_member_cannot_update_role(client: AsyncClient):
    owner = await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    member = await register_user(
        client,
        "member",
        "member@example.com",
    )

    another = await register_user(
        client,
        "another",
        "another@example.com",
    )

    project = await create_project(client)

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": another["public_id"],
        },
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "member",
            "password": "password123",
        },
    )

    response = await client.patch(
        f"/api/projects/{project['public_id']}/members/{another['public_id']}",
        json={
            "role": ProjectRole.ADMIN,
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_member_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.patch(
        f"/api/projects/{project['public_id']}/members/"
        "00000000-0000-0000-0000-000000000000",
        json={
            "role": ProjectRole.ADMIN,
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_member_success(client: AsyncClient):
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

    # Сейчас клиент, скорее всего, авторизован как member.
    client.cookies.clear()

    # Логинимся именно как owner
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Теперь проект принадлежит owner
    project = await create_project(client)

    # owner добавляет member
    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    assert response.status_code == 201

    # owner удаляет member
    response = await client.delete(
        f"/api/projects/{project['public_id']}/members/{member['public_id']}"
    )

    assert response.status_code == 204

    # Проверяем, что member действительно удалён
    response = await client.get(
        f"/api/projects/{project['public_id']}/members"
    )

    assert response.status_code == 200

    data = response.json()

    usernames = {
        item["user"]["username"]
        for item in data
    }

    assert "owner" in usernames
    assert "member" not in usernames


@pytest.mark.asyncio
async def test_member_cannot_delete_member(client: AsyncClient):
    owner = await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    member = await register_user(
        client,
        "member",
        "member@example.com",
    )

    another = await register_user(
        client,
        "another",
        "another@example.com",
    )

    project = await create_project(client)

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": another["public_id"],
        },
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "member",
            "password": "password123",
        },
    )

    response = await client.delete(
        f"/api/projects/{project['public_id']}/members/{another['public_id']}"
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_member_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.delete(
        f"/api/projects/{project['public_id']}/members/"
        "00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_members_invalid_project_uuid(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    response = await client.get(
        "/api/projects/not-a-uuid/members"
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_member_invalid_project_uuid(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    response = await client.post(
        "/api/projects/not-a-uuid/members",
        json={
            "user_public_id": "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_member_invalid_uuid(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.patch(
        f"/api/projects/{project['public_id']}/members/not-a-uuid",
        json={
            "role": ProjectRole.ADMIN,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_member_invalid_uuid(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.delete(
        f"/api/projects/{project['public_id']}/members/not-a-uuid"
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_add_member_without_permission(client: AsyncClient):
    # Первый пользователь — owner проекта
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    project_response = await client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test description",
        },
    )

    assert project_response.status_code == 201
    project_id = project_response.json()["public_id"]

    await client.post("/api/auth/logout")

    # Второй пользователь
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    user2_id = response.json()["public_id"]

    # user2 не является членом проекта и не имеет MEMBER_ADD
    response = await client.post(
        f"/api/projects/{project_id}/members",
        json={
            "user_public_id": user2_id,
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_member_already_in_project(client: AsyncClient):
    # Owner
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    project_response = await client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test description",
        },
    )

    assert project_response.status_code == 201
    project_id = project_response.json()["public_id"]

    # Второй пользователь
    await client.post("/api/auth/logout")

    response = await client.post(
        "/api/auth/register",
        json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    user2_id = response.json()["public_id"]

    # Возвращаемся под owner
    await client.post("/api/auth/logout")

    await client.post(
        "/api/auth/login",
        json={
            "username": "daniel",
            "password": "password123",
        },
    )

    # Первый раз добавляем
    response = await client.post(
        f"/api/projects/{project_id}/members",
        json={
            "user_public_id": user2_id,
        },
    )

    assert response.status_code == 201

    # Второй раз того же пользователя
    response = await client.post(
        f"/api/projects/{project_id}/members",
        json={
            "user_public_id": user2_id,
        },
    )

    assert response.status_code == 409