import aio_pika
from aio_pika.abc import AbstractChannel, AbstractExchange


class ExchangeManager:
    EVENTS_EXCHANGE = "issueflow.events"

    @classmethod
    async def get_events_exchange(cls, channel: AbstractChannel) -> AbstractExchange:
        return await channel.declare_exchange(
            cls.EVENTS_EXCHANGE,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )