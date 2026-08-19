from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models import Comment


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