from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Issue


class IssueRepository:
    @staticmethod
    async def create(db: AsyncSession,issue: Issue) -> Issue:
        db.add(issue)
        await db.flush()
        await db.refresh(issue)
        return issue

    @staticmethod
    async def get_by_public_id(db: AsyncSession,public_id: UUID) -> Issue | None:
        result = await db.execute(
            select(Issue).where(
                Issue.public_id == public_id,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_by_project(db: AsyncSession,project_id: int) -> list[Issue]:
        result = await db.execute(
            select(Issue).where(
                Issue.project_id == project_id,
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession,issue: Issue) -> Issue:
        await db.flush()
        await db.refresh(issue)
        return issue

    @staticmethod
    async def delete(db: AsyncSession, issue: Issue) -> Issue:
        issue.deleted_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(issue)

        return issue