from uuid import UUID

from fastapi import APIRouter, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.issue import schema as schema
from app.modules.issue.service import issue_service, issue_filters

router = APIRouter(prefix="/projects/{project_id}/issues",tags=["Issues"])


@router.post("",response_model=schema.IssueResponse,status_code=status.HTTP_201_CREATED)
async def create(project_id: UUID, data: schema.IssueCreate, user: CurrentUser, service: issue_service):
    return await service.create(project_id=project_id, data=data, user=user)


@router.get( "", response_model=list[schema.IssueResponse])
async def get_all(project_id: UUID, user: CurrentUser, service: issue_service, filters: issue_filters):
    return await service.list(project_id=project_id, user=user, filters=filters)


@router.get("/{issue_id}",response_model=schema.IssueResponseDetail)
async def get_one(user: CurrentUser, issue_id: UUID, service: issue_service):
    return await service.get(public_id=issue_id, user=user)


@router.patch("/{issue_id}", response_model=schema.IssueUpdateResponse)
async def update_issue(issue_id: UUID, data: schema.IssueUpdate, service: issue_service, user: CurrentUser):
    return await service.update(public_id=issue_id, data=data, user=user)


@router.patch("/{issue_id}/due-date",response_model=schema.IssueDueDateResponse)
async def update_due_date(issue_id: UUID, data: schema.IssueDueDateUpdate,service: issue_service,user: CurrentUser):
    return await service.update_due_date(issue_id=issue_id,data=data, user=user)


@router.patch("/{issue_id}/assignee",response_model=schema.IssueAssigneeResponse)
async def update_assignee(issue_id: UUID, data: schema.IssueAssigneeUpdate, service: issue_service, user: CurrentUser):
    return await service.update_assignee(issue_id=issue_id, data=data, user=user)


@router.patch("/{issue_id}/priority", response_model=schema.IssuePriorityResponse)
async def update_priority(issue_id: UUID, data: schema.IssuePriorityUpdate, service: issue_service, user: CurrentUser):
    return await service.update_priority(issue_id=issue_id, data=data, user=user)


@router.patch("/{issue_id}/status",response_model=schema.IssueStatusResponse)
async def update_status(issue_id: UUID, data: schema.IssueStatusUpdate, service: issue_service, user: CurrentUser):
    return await service.update_status(issue_id=issue_id, data=data, user=user)


@router.post("/{issue_id}/close",response_model=schema.IssueStatusResponse)
async def close_issue(issue_id: UUID, service: issue_service, user: CurrentUser):
    return await service.close(issue_id=issue_id, user=user)


@router.post("/{issue_id}/reopen",response_model=schema.IssueStatusResponse)
async def reopen_issue(issue_id: UUID, service: issue_service, user: CurrentUser):
    return await service.reopen(issue_id=issue_id, user=user)



@router.delete("/{issue_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete(issue_id: UUID, service: issue_service, user: CurrentUser):
    await service.delete(public_id=issue_id, user=user)