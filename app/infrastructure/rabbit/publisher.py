from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractExchange, AbstractRobustChannel

from app.events.schemas import Event
from app.infrastructure.rabbit.connection import RabbitConnection
from app.infrastructure.rabbit.exchanges import ExchangeManager



class RabbitPublisher:
    _channel: AbstractRobustChannel | None = None
    _exchange: AbstractExchange | None = None

    @classmethod
    async def connect(cls):
        if cls._channel and not cls._channel.is_closed:
            return

        cls._channel = await RabbitConnection.create_channel()
        cls._exchange = await ExchangeManager.get_events_exchange(cls._channel)

    @classmethod
    async def publish(cls, event: Event):
        if cls._exchange is None:
            await cls.connect()

        message = Message(body=event.model_dump_json().encode(),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT
        )

        await cls._exchange.publish(message=message, routing_key=event.ROUTING_KEY)

    @classmethod
    async def close(cls):
        if cls._channel and not cls._channel.is_closed:
            await cls._channel.close()