from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.events import CommentCreatedEvent, CommentDeletedEvent, CommentUpdatedEvent
from app.infrastructure.db.models import Comment, User
from app.infrastructure.rabbitmq import RabbitPublisher
from app.modules.auth.dependencies import DBSession
from app.modules.comments.repository import CommentRepository
from app.modules.comments.schema import CommentCreate, CommentResponse,CommentUpdate, CommentTreeResponse
from app.modules.issue.repository import IssueRepository
from app.permissions import PermissionContext, Permission, ProjectRBAC
from app.utils.func_utils import to, get_now_dt


class CommentService:
    def __init__(self,repository: CommentRepository, issue_repository: IssueRepository, db: AsyncSession):
        self.repository = repository
        self.issue_repository = issue_repository
        self.db = db

    @staticmethod
    def _to_comment_tree_node(comment: Comment) -> CommentTreeResponse:
        base = to(CommentResponse, comment)
        return CommentTreeResponse(**base.model_dump(), children=[])

    @staticmethod
    def build_comment_tree(comments: list[Comment]) -> list[CommentTreeResponse]:
        comment_map = {comment.id: CommentService._to_comment_tree_node(comment) for comment in comments}

        roots = []

        for comment in comments:
            dto = comment_map[comment.id]

            if comment.parent_comment_id is None:
                roots.append(dto)
            else:
                parent = comment_map.get(comment.parent_comment_id)
                if parent:
                    parent.children.append(dto)

        return roots

    async def create(self, issue_id: UUID, data: CommentCreate, user: User) -> CommentResponse:
        result = await self.issue_repository.get_by_public_id_with_current_member(self.db, issue_id, user.id)

        if result is None:
            raise AppException( ErrorCode.ISSUE_NOT_FOUND,"Issue not found")

        issue, member = result

        context = PermissionContext(user=user, project=issue.project, member=member)
        ProjectRBAC.require(permission=Permission.COMMENT_CREATE, context=context)

        parent_comment_id = None

        if data.parent_comment_public_id is not None:
            parent_comment = await self.repository.get_by_public_id(self.db, data.parent_comment_public_id)

            if parent_comment is None:
                raise AppException(ErrorCode.PARENT_COMMENT_NOT_FOUND, "Parent comment not found")

            if parent_comment.issue_id != issue.id:
                raise AppException(ErrorCode.PARENT_COMMENT_INVALID, "Parent comment belongs to another issue")

            parent_comment_id = parent_comment.id

        comment = Comment(
            issue_id=issue.id,
            author_id=user.id,
            parent_comment_id=parent_comment_id,
            content=data.content,
            author=user
        )

        comment = await self.repository.create(self.db, comment)
        await self.db.commit()

        event = CommentCreatedEvent.from_models(issue, user, comment)
        await RabbitPublisher.publish(event)

        return to(CommentResponse, comment)

    async def update(self, comment_id: UUID, data: CommentUpdate, user: User) -> CommentResponse:
        result = await self.repository.get_by_public_id_with_current_member(self.db, comment_id, user.id)

        if result is None:
            raise AppException(ErrorCode.COMMENT_NOT_FOUND,"Comment not found")

        comment, member = result

        context = PermissionContext(user=user, project=comment.issue.project, member=member, resource=comment)
        ProjectRBAC.require(permission=Permission.COMMENT_UPDATE, context=context)

        comment.content = data.content

        await self.db.commit()

        event = CommentUpdatedEvent.from_models(comment.issue, user, comment)
        await RabbitPublisher.publish(event)

        return to(CommentResponse, comment)

    async def delete(self, comment_id: UUID, user: User) -> None:
        result = await self.repository.get_by_public_id_with_current_member(self.db, comment_id, user.id)

        if result is None:
            raise AppException(ErrorCode.COMMENT_NOT_FOUND, "Comment not found")

        comment, member = result

        context = PermissionContext(user=user, project=comment.issue.project, member=member, resource=comment)
        ProjectRBAC.require(permission=Permission.COMMENT_DELETE, context=context)

        comment.deleted_at = get_now_dt()

        await self.db.commit()

        event = CommentDeletedEvent.from_models(comment.issue, user, comment)
        await RabbitPublisher.publish(event)


async def get_comments_service(db: DBSession) -> CommentService:
    return CommentService(repository=CommentRepository(), issue_repository=IssueRepository(), db=db)

comments_service = Annotated[CommentService, Depends(get_comments_service)]
    
    