from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.model_projects import Project


class ProjectRepository:
    @staticmethod
    async def create(db: AsyncSession,project: Project) -> Project:
        db.add(project)
        await db.flush()
        await db.refresh(project)
        return project

    @staticmethod
    async def get_by_public_id(db: AsyncSession,public_id: UUID) -> Project | None:
        result = await db.execute(
            select(Project).where(
                Project.public_id == public_id,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Project]:
        result = await db.execute(
            select(Project)
        )

        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession, project: Project) -> Project:
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