from uuid import UUID

from fastapi import APIRouter, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.issue.schema import IssueCreate,IssueResponse,IssueUpdate
from app.modules.issue.service import issue_service

router = APIRouter(prefix="/issues",tags=["Issues"])


@router.post("/projects/{project_id}",response_model=IssueResponse,status_code=status.HTTP_201_CREATED)
async def create_issue(project_id: UUID,data: IssueCreate,current_user: CurrentUser,service: issue_service):
    return await service.create(project_id=project_id,data=data,current_user=current_user)


@router.get( "/projects/{project_id}", response_model=list[IssueResponse])
async def get_all_issues(project_id: UUID,service: issue_service):
    return await service.get_all(project_id=project_id)


@router.get("/{issue_id}",response_model=IssueResponse)
async def get_issue(issue_id: UUID,service: issue_service,):
    return await service.get_by_public_id(public_id=issue_id)


@router.patch("/{issue_id}", response_model=IssueResponse)
async def update_issue(issue_id: UUID,data: IssueUpdate,service: issue_service):
    return await service.update(public_id=issue_id,data=data)


@router.delete("/{issue_id}",status_code=status.HTTP_204_NO_CONTENT,)
async def delete_issue(issue_id: UUID,service: issue_service):
    await service.delete(public_id=issue_id)