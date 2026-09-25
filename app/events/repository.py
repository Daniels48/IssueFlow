from datetime import timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


from app.infrastructure.db.models.model_outbox import OutboxStatus, OutboxEvent
from app.utils.func_utils import get_now_dt


MAX_ATTEMPTS = 5

RETRY_DELAYS = {
    1: 5,       # 5 секунд
    2: 30,      # 30 секунд
    3: 300,     # 5 минут
    4: 1800,    # 30 минут
    5: 3600,    # 1 час
}


class OutboxRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_pending(self, limit: int = 100) -> list[OutboxEvent]:
        result = await self.session.execute(
            select(OutboxEvent)
            .where(
                OutboxEvent.status == OutboxStatus.PENDING,
                OutboxEvent.available_at <= get_now_dt(),
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
                published_at=get_now_dt(),
            )
        )

    async def mark_failed(self,event_id: UUID,error: str) -> None:

        event = await self.session.get(OutboxEvent, event_id)

        if event is None:
            return

        attempts = event.attempts + 1

        if attempts >= MAX_ATTEMPTS:
            status = OutboxStatus.FAILED
            available_at = event.available_at

        else:
            status = OutboxStatus.PENDING
            available_at = (get_now_dt()+ timedelta(seconds=RETRY_DELAYS[attempts]))

        await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status=status,
                attempts=attempts,
                available_at=available_at,
                last_error=error,
            )
        )

    async def retry_failed(self, event_id: UUID) -> None:
        await self.session.execute(
            update(OutboxEvent)
            .where(
                OutboxEvent.id == event_id,
                OutboxEvent.status == OutboxStatus.FAILED,
            )
            .values(
                status=OutboxStatus.PENDING,
                available_at=get_now_dt(),
                last_error=None,
            )
        )