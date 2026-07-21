from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.infrastructure.db.models import Issue, Comment, Project, ProjectMember


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
                Issue.deleted_at.is_(None),
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_public_id_full(db: AsyncSession, public_id: UUID) -> Issue | None:
        stmt = (
            select(Issue)
            .options(
                selectinload(Issue.reporter),
                selectinload(Issue.assignee),
                selectinload(Issue.comments).selectinload(Comment.author),
                with_loader_criteria(
                    Comment,
                    Comment.deleted_at.is_(None),
                    include_aliases=True,
                ),
            )
            .where(
                Issue.public_id == public_id,
                Issue.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_public_id_edit(db: AsyncSession, public_id: UUID) -> Issue | None:
        stmt = (
            select(Issue)
            .options(
                selectinload(Issue.assignee),
                selectinload(Issue.project)
                .selectinload(Project.users),
            )
            .where(
                Issue.public_id == public_id,
                Issue.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()


    @staticmethod
    async def get_all_by_project(db: AsyncSession, project_id: int, user_id: int, query: str | None) -> list[Issue]:
        stmt = (
            select(Issue)
            .options(
                selectinload(Issue.reporter),
                selectinload(Issue.assignee),
            )
            .where(
                Issue.project_id == project_id,
                Issue.deleted_at.is_(None),
                or_(
                    Issue.assignee_id == user_id,
                    Issue.reporter_id == user_id,
                ),
            )
        )

        if query:
            stmt = stmt.where(Issue.title.ilike(f"%{query}%"))

        result = await db.execute(stmt)

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