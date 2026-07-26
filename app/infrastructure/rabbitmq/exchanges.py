from aio_pika import ExchangeType
from aio_pika.abc import AbstractExchange, AbstractChannel



class ExchangeManager:
    EVENTS_EXCHANGE = "issueflow.events"

    @classmethod
    async def get_events_exchange(cls, channel: AbstractChannel) -> AbstractExchange:
        return await channel.declare_exchange(
            cls.EVENTS_EXCHANGE,
            ExchangeType.TOPIC,
            durable=True,
        )