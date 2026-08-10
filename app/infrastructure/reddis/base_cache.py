import secrets
from uuid import UUID

from app.infrastructure.reddis.connection import RedisConnection


def _generate_verification_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class BaseCodeCache:
    PREFIX: str
    COOLDOWN_PREFIX: str

    TTL = 600
    COOLDOWN = 60

    @classmethod
    def _key(cls, user_id: UUID) -> str:
        return f"{cls.PREFIX}:{user_id}"

    @classmethod
    def _cooldown_key(cls, user_id: UUID) -> str:
        return f"{cls.COOLDOWN_PREFIX}:{user_id}"

    @classmethod
    async def set_cooldown(cls, user_id: UUID) -> None:
        redis = await RedisConnection.get_client()
        await redis.set(cls._cooldown_key(user_id), 1, ex=cls.COOLDOWN)

    @classmethod
    async def has_cooldown(cls, user_id: UUID) -> bool:
        redis = await RedisConnection.get_client()
        return bool(await redis.exists(cls._cooldown_key(user_id)))

    @classmethod
    async def set(cls, user_id: UUID, code: str) -> None:
        redis = await RedisConnection.get_client()
        await redis.set(cls._key(user_id), code, ex=cls.TTL)

    @classmethod
    async def get(cls, user_id: UUID) -> str | None:
        redis = await RedisConnection.get_client()
        return await redis.get(cls._key(user_id))

    @classmethod
    async def delete(cls, user_id: UUID) -> None:
        redis = await RedisConnection.get_client()
        await redis.delete(cls._key(user_id))

    @classmethod
    async def create(cls, user_id: UUID) -> str:
        code = _generate_verification_code()

        await cls.set(user_id, code)
        await cls.set_cooldown(user_id)

        return code