from uuid import UUID

from fastapi import APIRouter, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.comments.schema import CommentCreate, CommentUpdate, CommentResponseBase
from app.modules.comments.service import comments_service


router = APIRouter(prefix="/projects/{project_id}/issues/{issue_id}/comments",tags=["Comments"])


@router.post("",response_model=CommentResponseBase, status_code=status.HTTP_201_CREATED)
async def create_comment(issue_id: UUID, data: CommentCreate, current_user: CurrentUser, service: comments_service):
    return await service.create(issue_id=issue_id, data=data, user=current_user)

@router.patch("/{comment_id}",response_model=CommentResponseBase)
async def update_comment(comment_id: UUID, issue_id: UUID, data: CommentUpdate,current_user: CurrentUser,service: comments_service):
    return await service.update(comment_id=comment_id,data=data,current_user=current_user, issue_id=issue_id)

@router.delete("/{comment_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: UUID, issue_id: UUID, current_user: CurrentUser, service: comments_service):
    await service.delete(comment_id=comment_id, current_user=current_user, issue_id=issue_id)