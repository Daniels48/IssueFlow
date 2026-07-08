import aio_pika

from app.core.config import settings


class RabbitConnection:
    connection = None

    @classmethod
    async def connect(cls):
        cls.connection = await aio_pika.connect_robust(
            host=settings.rabbit.host,
            port=settings.rabbit.port,
            login=settings.rabbit.user,
            password=settings.rabbit.password,
        )

    @classmethod
    async def close(cls):
        if cls.connection:
            await cls.connection.close()