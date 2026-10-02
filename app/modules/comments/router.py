from uuid import UUID

from fastapi import APIRouter, status, Query

from app.modules.auth.dependencies import CurrentUser
from app.modules.comments import schema as schema
from app.modules.comments.service import comments_service, PageQuery, PerPageQuery

router = APIRouter(prefix="/projects/{project_id}/issues/{issue_id}/comments",tags=["Comments"])


@router.post("", response_model=schema.CommentCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(issue_id: UUID, data: schema.CommentCreate, user: CurrentUser, service: comments_service):
    return await service.create(issue_id=issue_id, data=data, user=user)

@router.get("",response_model=schema.CommentPageResponse)
async def get_comments(issue_id:UUID,user:CurrentUser,service:comments_service,page:PageQuery=1,per_page:PerPageQuery=20):
    return await service.get_comments(issue_id=issue_id,user=user, page=page, per_page=per_page)

@router.get("/{comment_id}/replies", response_model=schema.CommentPageResponse)
async def get_replies(comment_id:UUID,user:CurrentUser,service:comments_service,page:PageQuery=1,per_page:PerPageQuery=20):
    return await service.get_replies(comment_id=comment_id,user=user,page=page,per_page=per_page)

@router.patch("/{comment_id}",response_model=schema.CommentResponse)
async def update_comment(comment_id: UUID, data: schema.CommentUpdate, user: CurrentUser, service: comments_service):
    return await service.update(comment_id=comment_id,data=data, user=user)

@router.delete("/{comment_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: UUID, current_user: CurrentUser, service: comments_service):
    await service.delete(comment_id=comment_id, user=current_user)