from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, contains_eager

from app.infrastructure.db.models import Comment, ProjectMember, Issue, Project


class CommentRepository:
    @staticmethod
    async def create(db: AsyncSession, comment: Comment) -> Comment:
        db.add(comment)
        await db.flush()
        return comment

    @staticmethod
    async def get_by_public_id(db: AsyncSession, public_id: UUID) -> Comment:
        result = await db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(
                Comment.public_id == public_id,
                Comment.deleted_at.is_(None),
            )
        )

        return result.scalar_one()

    @staticmethod
    async def get_by_public_id_with_current_member(db: AsyncSession, public_id: UUID, user_id: int,
    ) -> tuple[Comment, ProjectMember | None] | None:
        stmt = (
            select(Comment, ProjectMember)
            .join(Comment.issue)
            .join(Issue.project)
            .outerjoin(
                ProjectMember,
                (ProjectMember.project_id == Project.id)
                & (ProjectMember.user_id == user_id),
            )
            .options(
                contains_eager(Comment.issue)
                .contains_eager(Issue.project)
            )
            .where(
                Comment.public_id == public_id,
                Comment.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)

        row = result.one_or_none()

        if row is None:
            return None

        comment, member_current = row

        return comment, member_current