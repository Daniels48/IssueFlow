import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel

from app.core.config import settings


class RabbitConnection:
    _connection: AbstractRobustConnection | None = None

    @classmethod
    async def get_connection(cls) -> AbstractRobustConnection:
        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await aio_pika.connect_robust(**settings.rabbit.model_dump())

        return cls._connection

    @classmethod
    async def create_channel(cls) -> AbstractRobustChannel:
        connection = await cls.get_connection()
        return await connection.channel()

    @classmethod
    async def close(cls) -> None:
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()