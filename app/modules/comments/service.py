from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.events import CommentCreatedEvent, CommentDeletedEvent, CommentUpdatedEvent, OutboxFactory
from app.core.exceptions import AppException, ErrorCode
from app.infrastructure.db.database import DBSession
from app.infrastructure.db.models import Comment, User
from app.modules.comments.repository import CommentRepository
from app.modules.comments import schema as schema
from app.modules.issue.repository import IssueRepository
from app.modules.issue.status import IssueStatus
from app.permissions import PermissionContext, Permission, ProjectRBAC
from app.utils.func_utils import to, get_now_dt


class CommentService:
    def __init__(self,repository: CommentRepository, issue_repository: IssueRepository, db: AsyncSession):
        self.repository = repository
        self.issue_repository = issue_repository
        self.db = db

    @staticmethod
    def _to_comment_tree_node(comment: Comment) -> schema.CommentTreeResponse:
        base = to(schema.CommentResponse, comment)
        return schema.CommentTreeResponse(**base.model_dump(), children=[])

    @staticmethod
    def build_comment_tree(comments: list[Comment]) -> list[schema.CommentTreeResponse]:
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

    async def create(self, issue_id: UUID, data: schema.CommentCreate, user: User) -> schema.CommentCreateResponse:
        result = await self.issue_repository.get_by_public_id_with_current_member(self.db, issue_id, user.id)

        if result is None:
            raise AppException( ErrorCode.ISSUE_NOT_FOUND,"Issue not found")

        issue, member = result

        context = PermissionContext(user=user, project=issue.project, member=member)
        ProjectRBAC.require(permission=Permission.COMMENT_CREATE, context=context)

        if issue.status == IssueStatus.CLOSED:
            raise AppException(ErrorCode.ISSUE_CLOSED,"Issue already closed")

        parent_comment = None
        parent_comment_id = None

        if data.parent_comment_public_id is not None:
            parent_comment = await self.repository.get_by_public_id(self.db, data.parent_comment_public_id)

            if parent_comment is None:
                raise AppException(ErrorCode.PARENT_COMMENT_NOT_FOUND, "Parent comment not found")

            if parent_comment.issue_id != issue.id:
                raise AppException(ErrorCode.PARENT_COMMENT_INVALID, "Parent comment belongs to another issue")

            parent_comment_id = parent_comment.id

        now = get_now_dt()

        comment = Comment(
            issue_id=issue.id,
            author_id=user.id,
            parent_comment_id=parent_comment_id,
            content=data.content,
            parent=parent_comment,
            author=user,
            created_at=now,
            updated_at=now,
        )

        comment = await self.repository.create(self.db, comment)

        event = CommentCreatedEvent.from_model(comment, user, issue, parent_comment, now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return schema.CommentCreateResponse(
            **to(schema.CommentResponse, comment).model_dump(),
            parent_comment_public_id=parent_comment.public_id if parent_comment else None,
        )

    async def update(self, comment_id: UUID, data: schema.CommentUpdate, user: User) -> schema.CommentResponse:
        result = await self.repository.get_by_public_id_with_current_member(self.db, comment_id, user.id)

        if result is None:
            raise AppException(ErrorCode.COMMENT_NOT_FOUND,"Comment not found")

        comment, member = result

        if comment.issue.status == IssueStatus.CLOSED:
            raise AppException(ErrorCode.ISSUE_CLOSED,"Issue already closed")

        context = PermissionContext(user=user, project=comment.issue.project, member=member, resource=comment)
        ProjectRBAC.require(permission=Permission.COMMENT_UPDATE, context=context)

        if comment.content == data.content:
            return to(schema.CommentResponse, comment)

        now = get_now_dt()

        old_content = comment.content
        comment.content = data.content
        comment.updated_at = now

        event = CommentUpdatedEvent.from_model(comment=comment, old_value=old_content,user=user,occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return to(schema.CommentResponse, comment)

    async def delete(self, comment_id: UUID, user: User) -> None:
        result = await self.repository.get_by_public_id_with_current_member(self.db, comment_id, user.id)

        if result is None:
            raise AppException(ErrorCode.COMMENT_NOT_FOUND, "Comment not found")

        comment, member = result

        if comment.issue.status == IssueStatus.CLOSED:
            raise AppException(ErrorCode.ISSUE_CLOSED,"Issue already closed")

        context = PermissionContext(user=user, project=comment.issue.project, member=member, resource=comment)
        ProjectRBAC.require(permission=Permission.COMMENT_DELETE, context=context)

        now = get_now_dt()

        comment.deleted_at = now

        event = CommentDeletedEvent.from_model(comment=comment,user=user,occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()


async def get_comments_service(db: DBSession) -> CommentService:
    return CommentService(repository=CommentRepository(), issue_repository=IssueRepository(), db=db)

comments_service = Annotated[CommentService, Depends(get_comments_service)]
    
    