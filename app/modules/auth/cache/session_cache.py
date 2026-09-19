from uuid import UUID

from app.core.config import settings
from app.infrastructure.reddis import RedisConnection, handle_redis_errors


class SessionCache:
    PREFIX = f"{settings.redis.prefix}:session"
    TTL = settings.security.refresh_token_expire_seconds

    @classmethod
    def _key(cls, session_id: UUID) -> str:
        return f"{cls.PREFIX}:{session_id}"

    @classmethod
    @handle_redis_errors
    async def set(cls, session_id: UUID) -> None:
        redis = await RedisConnection.get_client()
        await redis.set(cls._key(session_id),1,ex=cls.TTL)


    @classmethod
    @handle_redis_errors
    async def exists(cls, session_id: UUID) -> bool:
        redis = await RedisConnection.get_client()
        return bool(await redis.exists(cls._key(session_id)))


    @classmethod
    @handle_redis_errors
    async def delete(cls, session_id: UUID) -> None:
        redis = await RedisConnection.get_client()
        await redis.delete(cls._key(session_id))


    @classmethod
    @handle_redis_errors
    async def refresh(cls, session_id: UUID) -> bool:
        redis = await RedisConnection.get_client()
        return bool(await redis.expire(cls._key(session_id), cls.TTL,))