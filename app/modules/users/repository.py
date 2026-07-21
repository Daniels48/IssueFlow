from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import User, ProjectMember
from app.modules.projects.schema import UserShortResponse


class UserRepository:
    @staticmethod
    async def create(db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_public_id(db: AsyncSession, public_id: UUID) -> User | None:
        result = await db.execute(
            select(User).where(
                User.public_id == public_id,
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(
            select(User).where(
                User.id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list_users_in_project(db: AsyncSession, query: str, project_id: int, current_user_id:int) -> list[UserShortResponse]:
        stmt = select(User).where(
            User.username.ilike(f"%{query}%"),
            User.deleted_at.is_(None),
            User.id != current_user_id,
        )

        stmt = (
            stmt.outerjoin(
                ProjectMember,
                (ProjectMember.user_id == User.id)
                & (ProjectMember.project_id == project_id)
                & (ProjectMember.deleted_at.is_(None))
            )
            .where(ProjectMember.id.is_(None))
        )

        stmt = (
            stmt.order_by(User.username)
            .limit(5)
        )

        result = await db.execute(stmt)

        users = result.scalars().all()

        return [UserShortResponse.model_validate(user) for user in users]