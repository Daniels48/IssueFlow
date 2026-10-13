import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Project, ProjectMember


async def register_user(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "daniel",
            "email": "daniel@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_project_without_auth(client: AsyncClient):
    response = await client.post(
        "/api/projects",
        json={"name": "Test Project","description": "Test description"}
    )

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_project_success(client: AsyncClient,db_session: AsyncSession):
    await register_user(client)

    response = await client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test description",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Project"
    assert data["description"] == "Test description"

    assert "public_id" in data
    assert "created_at" in data
    assert "updated_at" in data

    result = await db_session.execute(select(Project).where(Project.public_id == data["public_id"]))

    project = result.scalar_one()

    assert project.name == "Test Project"
    assert project.description == "Test description"

    result = await db_session.execute(select(ProjectMember).where(ProjectMember.project_id == project.id))

    member = result.scalar_one()

    assert member.user_id == project.owner_id


@pytest.mark.asyncio
async def test_get_projects(client: AsyncClient):
    await register_user(client)

    response = await client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test description",
        },
    )

    assert response.status_code == 201

    response = await client.get("/api/projects")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1

    project = data[0]

    assert project["name"] == "Test Project"
    assert project["description"] == "Test description"

    assert "public_id" in project
    assert "owner" in project
    assert "members_count" in project
    assert "issues_count" in project
    assert "comments_count" in project


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient):
    await register_user(client)

    create_response = await client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test description",
        },
    )

    assert create_response.status_code == 201

    project = create_response.json()

    response = await client.get(
        f"/api/projects/{project['public_id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["public_id"] == project["public_id"]
    assert data["name"] == "Test Project"
    assert data["description"] == "Test description"

    assert "owner" in data
    assert "members" in data
    assert "roles" in data

    assert isinstance(data["members"], list)
    assert isinstance(data["roles"], list)


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient):
    await register_user(client)

    create_response = await client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Old description",
        },
    )

    assert create_response.status_code == 201

    project = create_response.json()

    response = await client.patch(
        f"/api/projects/{project['public_id']}",
        json={
            "name": "Updated Project",
            "description": "New description",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["public_id"] == project["public_id"]
    assert data["name"] == "Updated Project"
    assert data["description"] == "New description"
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient):
    await register_user(client)

    create_response = await client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test description",
        },
    )

    assert create_response.status_code == 201

    project = create_response.json()

    response = await client.delete(
        f"/api/projects/{project['public_id']}"
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_project_soft_delete(client: AsyncClient,db_session: AsyncSession):
    await register_user(client)

    create_response = await client.post(
        "/api/projects",
        json={
            "name": "Test Project",
            "description": "Test description",
        },
    )

    assert create_response.status_code == 201

    project_data = create_response.json()

    response = await client.delete(
        f"/api/projects/{project_data['public_id']}"
    )

    assert response.status_code == 204

    result = await db_session.execute(
        select(Project).where(
            Project.public_id == project_data["public_id"]
        )
    )

    project = result.scalar_one()

    assert project.deleted_at is not None


@pytest.mark.asyncio
async def test_get_projects_without_auth(client: AsyncClient):
    response = await client.get("/api/projects")

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient):
    await register_user(client)

    response = await client.get("/api/projects/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project_not_found(client: AsyncClient):
    await register_user(client)

    response = await client.patch(
        "/api/projects/00000000-0000-0000-0000-000000000000",
        json={
            "name": "Updated Project",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_not_found(client: AsyncClient):
    await register_user(client)

    response = await client.delete("/api/projects/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_project_invalid_name(client: AsyncClient):
    await register_user(client)

    response = await client.post(
        "/api/projects",
        json={
            "name": "ab",
            "description": "Test description",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_name_too_long(client: AsyncClient):
    await register_user(client)

    response = await client.post(
        "/api/projects",
        json={ "name": "a" * 101, "description": "Test description"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_description_too_long(client: AsyncClient):
    await register_user(client)

    response = await client.post(
        "/api/projects",
        json={"name": "Test Project", "description": "a" * 501}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_project_without_membership(client: AsyncClient):
    await register_user(client)

    response = await client.post("/api/projects",
        json={ "name": "Private Project","description": "Private description"}
    )

    assert response.status_code == 201

    project = response.json()

    client.cookies.clear()

    response = await client.post(
        "/api/auth/register",
        json={
            "username": "another",
            "email": "another@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    response = await client.get(f"/api/projects/{project['public_id']}")

    assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_create_project_without_auth(client: AsyncClient):
    response = await client.post(
        "/api/projects",
        json={"name": "Test project","description": "Description"}
    )

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_projects_without_auth(client: AsyncClient):
    response = await client.get("/api/projects")

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_project_without_auth(client: AsyncClient):
    response = await client.get("/api/projects/00000000-0000-0000-0000-000000000000")

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_update_project_without_auth(client: AsyncClient):
    response = await client.patch("/api/projects/00000000-0000-0000-0000-000000000000",json={"name": "Updated" })

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_delete_project_without_auth(client: AsyncClient):
    response = await client.delete("/api/projects/00000000-0000-0000-0000-000000000000")

    assert response.status_code in (401, 403)

@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient):
    response = await client.get("/api/projects/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_project_invalid_uuid(client: AsyncClient):
    response = await client.get("/api/projects/not-a-uuid")

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_project_invalid_uuid(client: AsyncClient):
    response = await client.patch("/api/projects/not-a-uuid",json={"name": "Updated"})

    assert response.status_code == 401