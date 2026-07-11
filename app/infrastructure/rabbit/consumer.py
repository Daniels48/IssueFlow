from collections.abc import Awaitable, Callable

from aio_pika import IncomingMessage
from aio_pika.abc import AbstractQueue

from app.infrastructure.rabbit.connection import RabbitConnection
from app.infrastructure.rabbit.exchanges import ExchangeManager


class RabbitConsumer:

    @classmethod
    async def subscribe(
        cls,
        queue_name: str,
        routing_key: str,
        handler: Callable[[IncomingMessage], Awaitable[None]],
    ):
        channel = await RabbitConnection.create_channel()

        await channel.set_qos(prefetch_count=10)

        exchange = await ExchangeManager.get_events_exchange(channel)

        queue: AbstractQueue = await channel.declare_queue(
            queue_name,
            durable=True,
        )

        await queue.bind(exchange, routing_key)

        await queue.consume(handler)