from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


from app.infrastructure.db.models.model_outbox import OutboxStatus, OutboxEvent


class OutboxRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_pending(self, limit: int = 100) -> list[OutboxEvent]:
        result = await self.session.execute(
            select(OutboxEvent)
            .where(
                OutboxEvent.status == OutboxStatus.PENDING,
                OutboxEvent.available_at <= datetime.now(timezone.utc),
            )
            .order_by(OutboxEvent.created_at)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def mark_published(self, event_id: UUID) -> None:
        await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status=OutboxStatus.PUBLISHED,
                published_at=datetime.now(timezone.utc),
            )
        )

    async def mark_failed(self, event_id: UUID,error: str) -> None:
        await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status=OutboxStatus.FAILED,
                attempts=OutboxEvent.attempts + 1,
                last_error=error,
            )
        )