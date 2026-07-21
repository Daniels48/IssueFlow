from typing import Any
from uuid import UUID

from sqlalchemy import select, func, and_, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.infrastructure.db.models import ProjectMember, Comment, Issue, User
from app.infrastructure.db.models.model_projects import Project


class ProjectRepository:
    @staticmethod
    async def create(db: AsyncSession,project: Project) -> Project:
        db.add(project)
        await db.flush()
        await db.refresh(project)
        return project

    @staticmethod
    async def get_by_public_id(db: AsyncSession, public_id: UUID, user_id: int) -> Project | None:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.issues).selectinload(Issue.reporter),
                selectinload(Project.issues).selectinload(Issue.assignee),

                with_loader_criteria(
                    ProjectMember,
                    ProjectMember.deleted_at.is_(None),
                    include_aliases=True,
                ),
                with_loader_criteria(
                    Issue,
                    Issue.deleted_at.is_(None),
                    include_aliases=True,
                ),
            )
            .join(
                ProjectMember,
                and_(
                    ProjectMember.project_id == Project.id,
                    ProjectMember.user_id == user_id,
                    ProjectMember.deleted_at.is_(None),
                ),
            )
            .where(
                Project.public_id == public_id,
                Project.deleted_at.is_(None),
            )
        )
        result = await db.execute(stmt)

        project = result.scalar_one_or_none()

        return project

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Project]:
        result = await db.execute(
            select(Project)
        )

        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession, project: Project | None) -> Project | None:
        await db.flush()
        await db.refresh(project)
        return project

    @staticmethod
    async def delete(db: AsyncSession,project: Project) -> None:
        await db.delete(project)

    @staticmethod
    async def get_all_by_owner(db: AsyncSession,owner_id: int) -> list[Project]:
        result = await db.execute(
            select(Project).where(
                Project.owner_id == owner_id,
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_all_by_user(db: AsyncSession,user_id: int) -> list[Row[tuple[Any, Any, Any, Any]]]:
        members_subq = (
            select(
                ProjectMember.project_id.label("project_id"),
                func.count(ProjectMember.id).label("members_count"),
            )
            .where(
                ProjectMember.deleted_at.is_(None),
            )
            .group_by(ProjectMember.project_id)
            .subquery()
        )

        issues_subq = (
            select(
                Issue.project_id.label("project_id"),
                func.count(Issue.id).label("issues_count"),
            )
            .where(
                Issue.deleted_at.is_(None),
            )
            .group_by(Issue.project_id)
            .subquery()
        )

        comments_subq = (
            select(
                Issue.project_id.label("project_id"),
                func.count(Comment.id).label("comments_count"),
            )
            .select_from(Issue)
            .outerjoin(
                Comment,
                and_(
                    Comment.issue_id == Issue.id,
                    Comment.deleted_at.is_(None),
                ),
            )
            .where(
                Issue.deleted_at.is_(None),
            )
            .group_by(Issue.project_id)
            .subquery()
        )

        stmt = (
            select(
                Project,
                func.coalesce(
                    members_subq.c.members_count,
                    0,
                ).label("members_count"),
                func.coalesce(
                    issues_subq.c.issues_count,
                    0,
                ).label("issues_count"),
                func.coalesce(
                    comments_subq.c.comments_count,
                    0,
                ).label("comments_count"),
            )
            .join(
                ProjectMember,
                and_(
                    ProjectMember.project_id == Project.id,
                    ProjectMember.user_id == user_id,
                    ProjectMember.deleted_at.is_(None),
                ),
            )
            .outerjoin(
                members_subq,
                members_subq.c.project_id == Project.id,
            )
            .outerjoin(
                issues_subq,
                issues_subq.c.project_id == Project.id,
            )
            .outerjoin(
                comments_subq,
                comments_subq.c.project_id == Project.id,
            )
            .where(
                Project.deleted_at.is_(None),
            )
            .order_by(Project.created_at.desc())
        )

        result = await db.execute(stmt)

        return list(result.all())

    @staticmethod
    async def get_by_public_id_no_full(db: AsyncSession, public_id: UUID) -> Project | None:
        stmt = (
            select(Project)
            .where(
                Project.public_id == public_id,
                Project.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()