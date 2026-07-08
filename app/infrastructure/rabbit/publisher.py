import json

import aio_pika
from pydantic import BaseModel

from app.infrastructure.rabbit.connection import RabbitConnection


class RabbitPublisher:
    EXCHANGE_NAME = "issueflow.events"

    @classmethod
    async def publish(cls, event: BaseModel) -> None:
        if RabbitConnection.connection is None:
            raise RuntimeError("RabbitMQ is not connected")

        channel = await RabbitConnection.connection.channel()

        exchange = await channel.declare_exchange(
            cls.EXCHANGE_NAME,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        routing_key = event.__class__.__name__

        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(
                    event.model_dump(mode="json")
                ).encode(),
                content_type="application/json",
            ),
            routing_key=routing_key,
        )

        await channel.close()