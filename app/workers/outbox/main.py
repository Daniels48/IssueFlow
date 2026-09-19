import asyncio
import logging

from app.events.repository import OutboxRepository
from app.infrastructure.db.database import AsyncSessionLocal, engine
from app.infrastructure.rabbitmq import RabbitConnection
from app.infrastructure.rabbitmq.publisher import RabbitPublisher


logger = logging.getLogger(__name__)


POLL_INTERVAL = 1
BATCH_SIZE = 100


async def process_events() -> None:
    async with AsyncSessionLocal() as session:
        repository = OutboxRepository(session)

        events = await repository.get_pending(limit=BATCH_SIZE)

        if not events:
            return

        for event in events:
            try:
                await RabbitPublisher.publish(event)
                await repository.mark_published(event.id)
                await session.commit()

                logger.info("Outbox event published: %s",event.id)

            except Exception as error:
                await session.rollback()
                logger.exception("Failed to publish outbox event: %s",event.id)

                try:
                    await repository.mark_failed(event.id,str(error))
                    await session.commit()

                except Exception:
                    await session.rollback()
                    logger.exception("Failed to mark outbox event as failed: %s",event.id)


async def main() -> None:
    logger.info("Starting Outbox Worker")

    await RabbitPublisher.connect()

    try:
        while True:
            try:
                await process_events()

            except Exception:
                logger.exception("Outbox worker iteration failed")

            await asyncio.sleep(POLL_INTERVAL)

    finally:
        await RabbitPublisher.close()
        await RabbitConnection.close()

        await engine.dispose()

        logger.info("Outbox Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())