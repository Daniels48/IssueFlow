from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.model_session import Session
from app.utils.func_utils import get_now_dt


class SessionRepository:
    @staticmethod
    async def create(db: AsyncSession, session: Session) -> Session:
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_by_refresh_hash(db: AsyncSession, refresh_token_hash: str) -> Session | None:
        stmt = (
            select(Session)
            .where(Session.refresh_token_hash == refresh_token_hash)
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, session: Session) -> Session:
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def delete(db: AsyncSession, session: Session | None) -> None:
        session.deleted_at = get_now_dt()
        await db.commit()

    @staticmethod
    async def revoke_all(db: AsyncSession, user_id) -> None:
        stmt = (
            select(Session)
            .where(
                Session.user_id == user_id,
                Session.deleted_at.is_(None),
            )
        )

        result = await db.execute(stmt)
        sessions = result.scalars().all()
        now = get_now_dt()

        for session in sessions:
            session.revoked_at = now

        await db.commit()

    @staticmethod
    async def revoke(db: AsyncSession, session: Session) -> None:
        if session is not None:
            await db.delete(session)
            await db.commit()

    @staticmethod
    async def delete_expired(db: AsyncSession) -> None:
        stmt = delete(Session).where(
            Session.expires_at < datetime.utcnow()
        )

        await db.execute(stmt)
        await db.commit()