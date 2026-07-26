from redis.asyncio import Redis

from app.core.config import settings


class RedisConnection:
    _client: Redis | None = None

    @classmethod
    async def connect(cls) -> Redis:
        if cls._client is None:
            cls._client = Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db,
                password=settings.redis.password,
                socket_connect_timeout=settings.redis.socket_connect_timeout,
                socket_timeout=settings.redis.socket_timeout,
                health_check_interval=settings.redis.health_check_interval,
                decode_responses=True,
            )

            try:
                await cls._client.ping()
            except Exception:
                await cls._client.aclose()
                raise

        return cls._client

    @classmethod
    async def get_client(cls) -> Redis:
        if cls._client is None:
            return await cls.connect()

        return cls._client

    @classmethod
    async def close(cls) -> None:
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None