import pytest
from httpx import AsyncClient

from app.modules.issue.priority import IssuePriority
from app.modules.issue.status import IssueStatus
from tests.test_members import create_project, register_user


@pytest.mark.asyncio
async def test_create_issue_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
            "description": "Test description",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test issue"
    assert data["description"] == "Test description"
    assert data["status"] == IssueStatus.OPEN
    assert data["priority"] == IssuePriority.MEDIUM
    assert data["reporter"]["username"] == "owner"
    assert data["assignee"] is None


@pytest.mark.asyncio
async def test_create_issue_without_auth(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    client.cookies.clear()

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_issue_project_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    response = await client.post(
        "/api/projects/00000000-0000-0000-0000-000000000000/issues",
        json={
            "title": "Test issue",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_issue_invalid_project_uuid(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    response = await client.post(
        "/api/projects/not-a-uuid/issues",
        json={
            "title": "Test issue",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_non_member_cannot_create_issue(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    await register_user(
        client,
        "other",
        "other@example.com",
    )

    client.cookies.clear()

    await client.post(
        "/api/auth/login",
        json={
            "username": "other",
            "password": "password123",
        },
    )

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_issue_with_assignee(client: AsyncClient):
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

    # Логинимся владельцем проекта
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Проект создаётся owner'ом
    project = await create_project(client)

    # Добавляем member в проект
    response = await client.post(
        f"/api/projects/{project['public_id']}/members",
        json={
            "user_public_id": member["public_id"],
        },
    )

    assert response.status_code == 201

    # Owner создаёт issue и назначает member
    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Assigned issue",
            "assignee_id": member["public_id"],
        },
    )


    assert response.status_code == 201

    data = response.json()

    assert data["assignee"]["public_id"] == member["public_id"]
    assert data["assignee"]["username"] == "member"


@pytest.mark.asyncio
async def test_create_issue_assignee_not_project_member(client: AsyncClient):
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

    # Явно логинимся owner
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Проект принадлежит owner
    project = await create_project(client)

    # other НЕ добавляем в проект

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
            "assignee_id": other["public_id"],
        },
    )


    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_issue_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
            "description": "Description",
        },
    )

    assert response.status_code == 201

    issue = response.json()

    response = await client.get(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["public_id"] == issue["public_id"]
    assert data["title"] == "Test issue"
    assert data["description"] == "Description"
    assert data["status"] == IssueStatus.OPEN
    assert data["priority"] == IssuePriority.MEDIUM
    assert "members" in data
    assert "allowed_statuses" in data
    assert "priorities" in data


@pytest.mark.asyncio
async def test_get_issue_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.get(
        f"/api/projects/{project['public_id']}/issues/"
        "00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_issue_without_membership(client: AsyncClient):
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

    # Явно логиним owner
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

    # owner создаёт issue
    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Private issue",
        },
    )

    assert response.status_code == 201

    issue = response.json()

    # Теперь логиним member, которого НЕ добавляли в проект
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "member",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    response = await client.get(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}"
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_issue_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Old title",
            "description": "Old description",
        },
    )

    issue = response.json()

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}",
        json={
            "title": "New title",
            "description": "New description",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["public_id"] == issue["public_id"]
    assert data["title"] == "New title"
    assert data["description"] == "New description"


@pytest.mark.asyncio
async def test_update_issue_not_found(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    response = await client.patch(
        "/api/projects/00000000-0000-0000-0000-000000000000/issues/"
        "00000000-0000-0000-0000-000000000000",
        json={
            "title": "New title",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_issue_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.delete(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}"
    )

    assert response.status_code == 204

    response = await client.get(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_issue_without_permission(client: AsyncClient):
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

    # Явно логиним owner
    client.cookies.clear()

    response = await client.post(
        "/api/auth/login",
        json={
            "username": "owner",
            "password": "password123",
        },
    )

    assert response.status_code == 204

    # Проект принадлежит owner
    project = await create_project(client)

    # owner создаёт issue
    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    assert response.status_code == 201

    issue = response.json()

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

    # member НЕ является членом проекта
    response = await client.delete(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}"
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_due_date_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/due-date",
        json={
            "due_date": "2030-01-01T12:00:00Z",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["due_date"].startswith("2030-01-01")


@pytest.mark.asyncio
async def test_update_due_date_invalid_past(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/due-date",
        json={
            "due_date": "2020-01-01T12:00:00Z",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_priority_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/priority",
        json={
            "priority": IssuePriority.HIGH,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["priority"] == IssuePriority.HIGH


@pytest.mark.asyncio
async def test_update_status_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    assert response.status_code == 201

    issue = response.json()

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/status",
        json={
            "status": IssueStatus.IN_PROGRESS,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == IssueStatus.IN_PROGRESS
    assert data["allowed_statuses"]["previous"] == IssueStatus.OPEN
    assert data["allowed_statuses"]["current"] == IssueStatus.IN_PROGRESS
    assert data["allowed_statuses"]["next"] == IssueStatus.REVIEW


@pytest.mark.asyncio
async def test_update_status_invalid_transition(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/status",
        json={
            "status": IssueStatus.CLOSED,
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_close_issue_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
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
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/close"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == IssueStatus.CLOSED


@pytest.mark.asyncio
async def test_close_issue_already_closed(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.post(f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/close")

    assert response.status_code == 200

    response = await client.post(f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/close")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reopen_issue_success(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    await client.post(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/close"
    )

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/reopen"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == IssueStatus.OPEN


@pytest.mark.asyncio
async def test_reopen_issue_not_closed(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
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
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/reopen"
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_closed_issue_cannot_be_updated(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    await client.post(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/close"
    )

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}",
        json={
            "title": "Changed",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unassign_issue_success(client: AsyncClient):
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
            "assignee_id": member["public_id"],
        },
    )

    issue = response.json()

    assert issue["assignee"]["public_id"] == member["public_id"]

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/assignee",
        json={
            "assignee_id": None,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["assignee"] is None

@pytest.mark.asyncio
async def test_update_status_flow(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    issue_url = (
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/status"
    )

    for status in [
        IssueStatus.IN_PROGRESS,
        IssueStatus.REVIEW,
        IssueStatus.DONE,
    ]:
        response = await client.patch(
            issue_url,
            json={"status": status},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == status


@pytest.mark.asyncio
async def test_update_status_invalid_transition(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    response = await client.patch(
        f"/api/projects/{project['public_id']}/issues/{issue['public_id']}/status",
        json={
            "status": IssueStatus.REVIEW,
        },
    )

    assert response.status_code == 400

@pytest.mark.asyncio
async def test_update_status_backward_transition(client: AsyncClient):
    await register_user(
        client,
        "owner",
        "owner@example.com",
    )

    project = await create_project(client)

    response = await client.post(
        f"/api/projects/{project['public_id']}/issues",
        json={
            "title": "Test issue",
        },
    )

    issue = response.json()

    issue_url = (
        f"/api/projects/{project['public_id']}/issues/"
        f"{issue['public_id']}/status"
    )

    response = await client.patch(
        issue_url,
        json={"status": IssueStatus.IN_PROGRESS},
    )
    assert response.status_code == 200

    response = await client.patch(
        issue_url,
        json={"status": IssueStatus.REVIEW},
    )
    assert response.status_code == 200

    response = await client.patch(
        issue_url,
        json={"status": IssueStatus.IN_PROGRESS},
    )

    assert response.status_code == 200
    assert response.json()["status"] == IssueStatus.IN_PROGRESS