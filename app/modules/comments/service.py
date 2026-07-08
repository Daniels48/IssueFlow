from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import User, Comment
from app.modules.auth.dependencies import DBSession
from app.modules.comments.repository import CommentRepository
from app.modules.comments.schema import CommentCreate, CommentUpdate
from app.modules.issue.repository import IssueRepository


class CommentService:
    def __init__(self,repository: CommentRepository,issue_repository: IssueRepository, db: AsyncSession):
        self.repository = repository
        self.issue_repository = issue_repository
        self.db = db

    async def create(self,issue_id: UUID,data: CommentCreate, current_user: User) -> Comment:
        issue = await self.issue_repository.get_by_public_id(self.db, issue_id)

        if not issue:
            raise ValueError("Issue not found")

        parent_comment = None

        if data.parent_comment_id:
            parent_comment = await self.repository.get_by_public_id( self.db, data.parent_comment_id)

            if not parent_comment:
                raise ValueError("Parent comment not found")

            if parent_comment.issue_id != issue.id:
                raise ValueError(
                    "Parent comment belongs to another issue"
                )

        comment = Comment(
            issue_id=issue.id,
            author_id=current_user.id,
            parent_comment_id=(
                parent_comment.id if parent_comment else None
            ),
            content=data.content,
        )

        comment = await self.repository.create(self.db,comment)
        await self.db.commit()
        return comment

    async def update(self,comment_id: UUID,data: CommentUpdate,current_user: User) -> Comment:
        comment = await self.repository.get_by_public_id(self.db, comment_id)

        if not comment:
            raise ValueError("Comment not found")

        if comment.author_id != current_user.id:
            raise ValueError("Permission denied")

        comment.content = data.content

        comment = await self.repository.update(self.db,comment)

        await self.db.commit()

        return comment

    async def delete(self,comment_id: UUID,current_user: User) -> None:
        comment = await self.repository.get_by_public_id(self.db,comment_id)

        if not comment:
            raise ValueError("Comment not found")

        if comment.author_id != current_user.id:
            raise ValueError("Permission denied")

        await self.repository.delete(self.db,comment,)
        await self.db.commit()


async def get_comments_service(db: DBSession) -> CommentService:
    return CommentService(repository=CommentRepository(), issue_repository=IssueRepository(),db=db)

comments_service = Annotated[CommentService, Depends(get_comments_service)]
    
    