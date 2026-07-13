import asyncio

from app.infrastructure.rabbit.connection import RabbitConnection
from app.infrastructure.rabbit.consumer import RabbitConsumer

from workers.event_worker.handlers.issue import issue_created_handler


async def main():
    await RabbitConnection.connect()

    await RabbitConsumer.subscribe(
        queue_name="event-worker",
        routing_key="issue.created",
        handler=issue_created_handler,
    )

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())