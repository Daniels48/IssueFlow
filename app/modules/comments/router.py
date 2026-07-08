from uuid import UUID

from fastapi import APIRouter, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.comments.schema import CommentCreate,CommentResponse,CommentUpdate
from app.modules.comments.service import comments_service

router = APIRouter(tags=["Comments"])


@router.post("/issues/{issue_id}/comments",response_model=CommentResponse,status_code=status.HTTP_201_CREATED,)
async def create_comment(issue_id: UUID,data: CommentCreate,current_user: CurrentUser,service: comments_service):
    return await service.create(issue_id=issue_id,data=data,current_user=current_user)


# @router.get("/issues/{issue_id}/comments",response_model=list[CommentResponse],)
# async def get_comments(issue_id: UUID,service: comments_service):
#     return await service.get_all(issue_id=issue_id)


@router.patch("/comments/{comment_id}",response_model=CommentResponse)
async def update_comment(comment_id: UUID,data: CommentUpdate,current_user: CurrentUser,service: comments_service):
    return await service.update(comment_id=comment_id,data=data,current_user=current_user,)


@router.delete("/comments/{comment_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: UUID,current_user: CurrentUser,service: comments_service):
    await service.delete(comment_id=comment_id,current_user=current_user)