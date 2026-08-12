from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.model_session import Session


class SessionRepository:
    @staticmethod
    async def create(db: AsyncSession, session: Session) -> Session:
        db.add(session)
        await db.flush()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_by_refresh_hash(db: AsyncSession, refresh_token_hash: str) -> Session | None:
        stmt = select(Session).where(
            Session.refresh_token_hash == refresh_token_hash
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_session_id(db: AsyncSession, session_id: UUID) -> Session | None:
        stmt = select(Session).where(
            Session.public_id == session_id,
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list_active_by_user_id(db: AsyncSession, user_id: int, now: datetime) -> list[Session]:
        stmt = (
            select(Session)
            .where(
                Session.user_id == user_id,
                Session.deleted_at.is_(None),
                Session.expires_at > now,
            )
            .order_by(Session.updated_at.desc())
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())