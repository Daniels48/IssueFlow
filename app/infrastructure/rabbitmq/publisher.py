from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractExchange, AbstractRobustChannel

from app.infrastructure.rabbitmq.events import Event
from app.infrastructure.rabbitmq.connection import RabbitConnection
from app.infrastructure.rabbitmq.exchanges import ExchangeManager


class RabbitPublisher:
    _channel: AbstractRobustChannel | None = None
    _exchange: AbstractExchange | None = None

    @classmethod
    async def connect(cls) -> None:
        if cls._channel and not cls._channel.is_closed:
            return

        cls._channel = await RabbitConnection.create_channel()
        cls._exchange = await ExchangeManager.get_events_exchange(cls._channel)

    @classmethod
    async def publish(cls, event: Event) -> None:
        if cls._exchange is None:
            await cls.connect()

        message = Message(
            body=event.model_dump_json().encode("utf-8"),
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        await cls._exchange.publish(message, routing_key=event.ROUTING_KEY)

    @classmethod
    async def close(cls) -> None:
        if cls._channel and not cls._channel.is_closed:
            await cls._channel.close()