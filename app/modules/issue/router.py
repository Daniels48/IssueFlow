from uuid import UUID

from fastapi import APIRouter, status, Query

from app.modules.auth.dependencies import CurrentUser
from app.modules.issue.schema import IssueCreate, IssueResponse, IssueUpdate, IssueResponseDetail, IssueResponseEdit, \
    IssueDueDateUpdate, IssueAssigneeUpdate, IssueStatusUpdate, IssuePriorityUpdate, IssueResponseStatus
from app.modules.issue.service import issue_service


router = APIRouter(prefix="/projects/{project_id}/issues",tags=["Issues"])


@router.post("",response_model=IssueResponse,status_code=status.HTTP_201_CREATED)
async def create(project_id: UUID, data: IssueCreate, current_user: CurrentUser, service: issue_service):
    return await service.create(project_id=project_id, data=data, user=current_user)


@router.get( "", response_model=list[IssueResponse])
async def get_all(
    project_id: UUID,
    current_user: CurrentUser,
    service: issue_service,
    search: str | None = Query(default=None, min_length=1),
):
    return await service.list(project_id=project_id, user=current_user, search=search)


@router.get("/{issue_id}",response_model=IssueResponseDetail)
async def get_one(project_id: UUID, current_user: CurrentUser, issue_id: UUID, service: issue_service):
    return await service.get(public_id=issue_id, user=current_user)


@router.get("/{issue_id}/edit",response_model=IssueResponseEdit)
async def get_issue_edit(project_id: UUID, user: CurrentUser, issue_id: UUID, service: issue_service):
    return await service.get_edit(public_id=issue_id, user=user)


@router.patch("/{issue_id}/due-date",response_model=IssueResponse)
async def update_due_date(issue_id: UUID, data: IssueDueDateUpdate,service: issue_service,user: CurrentUser):
    return await service.update_due_date(issue_id=issue_id,data=data, user=user)


@router.patch("/{issue_id}", response_model=IssueResponse)
async def update(issue_id: UUID, data: IssueUpdate, service: issue_service, user: CurrentUser):
    return await service.update(public_id=issue_id, data=data, user=user)


@router.delete("/{issue_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete(project_id: UUID, issue_id: UUID,service: issue_service, user: CurrentUser):
    await service.delete(public_id=issue_id, user=user)



@router.patch("/{issue_id}/due-date",response_model=IssueResponse)
async def update_due_date(issue_id: UUID, data: IssueDueDateUpdate,service: issue_service, user: CurrentUser):
    return await service.update_due_date(issue_id=issue_id, data=data, user=user)

@router.patch("/{issue_id}/assignee",response_model=IssueResponse)
async def update_assignee(issue_id: UUID, data: IssueAssigneeUpdate, service: issue_service, user: CurrentUser):
    return await service.update_assignee(issue_id=issue_id, data=data, user=user)

@router.patch("/{issue_id}/priority", response_model=IssueResponse)
async def update_priority(issue_id: UUID, data: IssuePriorityUpdate, service: issue_service, user: CurrentUser):
    return await service.update_priority(issue_id=issue_id, data=data, user=user)

@router.patch("/{issue_id}/status",response_model=IssueResponseStatus)
async def update_status(issue_id: UUID, data: IssueStatusUpdate, service: issue_service, user: CurrentUser):
    return await service.update_status(issue_id=issue_id, data=data, user=user)

@router.post("/{issue_id}/close",response_model=IssueResponse)
async def close_issue(issue_id: UUID, service: issue_service, user: CurrentUser):
    return await service.close(issue_id=issue_id, user=user)

@router.post("/{issue_id}/reopen",response_model=IssueResponse)
async def reopen_issue(issue_id: UUID, service: issue_service, user: CurrentUser):
    return await service.reopen(issue_id=issue_id, user=user)