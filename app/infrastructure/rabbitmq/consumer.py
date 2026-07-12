from collections.abc import Awaitable, Callable
from typing import Any

from aio_pika.abc import AbstractIncomingMessage,AbstractQueue, AbstractRobustChannel

from app.infrastructure.rabbitmq.connection import RabbitConnection
from app.infrastructure.rabbitmq.exchanges import ExchangeManager


class RabbitConsumer:

    @classmethod
    async def subscribe(
        cls,
        queue_name: str,
        routing_key: str,
        handler: Callable[[AbstractIncomingMessage], Awaitable[Any]],
    ) -> AbstractRobustChannel:

        channel = await RabbitConnection.create_channel()

        await channel.set_qos(prefetch_count=10)

        exchange = await ExchangeManager.get_events_exchange(channel)

        queue: AbstractQueue = await channel.declare_queue(queue_name, durable=True)

        await queue.bind(exchange, routing_key=routing_key)

        async def on_message(message: AbstractIncomingMessage):
            async with message.process(requeue=True):
                await handler(message)

        await queue.consume(on_message, exclusive=False, no_ack=False)

        return channel