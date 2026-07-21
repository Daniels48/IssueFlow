from uuid import UUID

from fastapi import APIRouter, status, Query

from app.modules.auth.dependencies import CurrentUser
from app.modules.issue.schema import IssueCreate, IssueResponse, IssueUpdate, IssueResponseDetail, IssueResponseEdit
from app.modules.issue.service import issue_service


router = APIRouter(prefix="/projects/{project_id}/issues",tags=["Issues"])


@router.post("",response_model=IssueResponse,status_code=status.HTTP_201_CREATED)
async def create_issue(project_id: UUID,data: IssueCreate, current_user: CurrentUser,service: issue_service):
    return await service.create(project_id=project_id, data=data, user=current_user)


@router.get( "", response_model=list[IssueResponse])
async def get_all_issues(
    project_id: UUID,
    current_user: CurrentUser,
    service: issue_service,
    query: str | None = Query(default=None, min_length=1),
):
    return await service.list(project_id=project_id, user=current_user, query=query)


@router.get("/{issue_id}",response_model=IssueResponseDetail)
async def get_issue(project_id: UUID, issue_id: UUID, service: issue_service):
    return await service.get(public_id=issue_id)


@router.get("/{issue_id}/edit",response_model=IssueResponseEdit)
async def get_issue_edit(project_id: UUID, issue_id: UUID, service: issue_service):
    return await service.get_edit(public_id=issue_id)


@router.patch("/{issue_id}", response_model=IssueResponse)
async def update_issue(project_id: UUID, issue_id: UUID, data: IssueUpdate, service: issue_service):
    return await service.update(public_id=issue_id, data=data)


@router.delete("/{issue_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(project_id: UUID, issue_id: UUID,service: issue_service):
    await service.delete(public_id=issue_id)