from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models import Comment


class CommentRepository:
    @staticmethod
    async def create(db: AsyncSession,comment: Comment) -> Comment:
        db.add(comment)
        await db.flush()
        await db.refresh(comment)
        return comment

    @staticmethod
    async def get_by_public_id_issue(db: AsyncSession, public_id: UUID) -> Comment | None:
        result = await db.execute(
            select(Comment).where(
                Comment.public_id == public_id,
                Comment.deleted_at.is_(None),
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_issue(db: AsyncSession,issue_id: int) -> list[Comment]:
        result = await db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(
                Comment.issue_id == issue_id,
                Comment.deleted_at.is_(None),
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_all_by_issue(db: AsyncSession,issue_id: int) -> list[Comment]:
        result = await db.execute(
            select(Comment).where(
                Comment.issue_id == issue_id,
                Comment.deleted_at.is_(None),
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession,comment: Comment) -> Comment:
        await db.flush()
        await db.refresh(comment)
        return comment


    @staticmethod
    async def delete(db: AsyncSession,comment: Comment) -> Comment:
        comment.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(comment)

        return comment