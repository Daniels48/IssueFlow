import json

from aio_pika import DeliveryMode, Message

from app.events import Event
from app.infrastructure.db.models import OutboxEvent
from app.infrastructure.rabbitmq.exchanges import ExchangeManager
from app.infrastructure.rabbitmq.connection import RabbitConnection

class RabbitPublisher:
    _channel = None
    _exchange = None

    @classmethod
    async def connect(cls) -> None:
        if cls._channel and not cls._channel.is_closed:
            return

        cls._channel = await RabbitConnection.create_channel()
        cls._exchange = await ExchangeManager.get_events_exchange(cls._channel)

    @classmethod
    async def publish(cls, event: OutboxEvent) -> None:
        if (
                cls._channel is None
                or cls._channel.is_closed
                or cls._exchange is None
        ):
            await cls.connect()

        message = Message(
            body=json.dumps(
                {
                    "event_id": str(event.id),
                    "event_type": event.event_type,
                    "aggregate_type": event.aggregate_type,
                    "aggregate_id": str(event.aggregate_id),
                    "payload": event.payload,
                    "occurred_at": event.occurred_at.isoformat(),
                }
            ).encode("utf-8"),
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        await cls._exchange.publish(message, routing_key=event.event_type)

    @classmethod
    async def close(cls) -> None:
        if cls._channel and not cls._channel.is_closed:
            await cls._channel.close()
            cls._channel = None
            cls._exchange = None