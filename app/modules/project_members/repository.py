from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models import ProjectMember


class ProjectMemberRepository:
    @staticmethod
    async def create(db: AsyncSession,member: ProjectMember) -> ProjectMember:
        db.add(member)
        await db.flush()
        await db.refresh(member)
        return member

    @staticmethod
    async def get_by_project_and_user(db: AsyncSession, project_id: int, user_id: int) -> ProjectMember | None:
        result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_by_project(db: AsyncSession, project_id: int) -> list[ProjectMember]:
        result = await db.execute(
            select(ProjectMember)
            .options(
                selectinload(ProjectMember.user)
            )
            .where(
                ProjectMember.project_id == project_id,
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession,member: ProjectMember) -> ProjectMember:
        await db.flush()
        await db.refresh(member)
        return member

    @staticmethod
    async def delete(db: AsyncSession,member: ProjectMember) -> None:
        await db.delete(member)

    @staticmethod
    async def user_in_project(db: AsyncSession, project_id: int, user_id: int) -> ProjectMember | None:
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.deleted_at.is_(None),
        )

        result = await db.execute(stmt)
        member = result.scalar_one_or_none()

        return member



