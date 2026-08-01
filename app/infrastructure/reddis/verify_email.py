import secrets
from uuid import UUID

from app.core.config import settings

from .connection import RedisConnection


def _generate_verification_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class VerifyEmailCache:
    PREFIX = f"{settings.redis.prefix}:verify_email"
    COOLDOWN_PREFIX = f"{settings.redis.prefix}:verify_email_cooldown"
    TTL = 600  # 10 минут
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
        await redis.set(cls._cooldown_key(user_id), 1, ex=60)

    @classmethod
    async def has_cooldown(cls, user_id: UUID) -> bool:
        redis = await RedisConnection.get_client()
        return bool(await redis.exists(cls._cooldown_key(user_id)))

    # if await VerifyEmailCache.has_cooldown(user.public_id):
    #     raise TooManyRequestsException()
    #
    # code = generate_verification_code()
    #
    # await VerifyEmailCache.set(user.public_id, code)
    #
    # await VerifyEmailCache.set_cooldown(user.public_id)
    #
    # send_email_task.delay(...)

    @classmethod
    async def set(cls,user_id: UUID,code: str,) -> None:
        redis = await RedisConnection.get_client()

        await redis.set(cls._key(user_id), code, ex=cls.TTL)

    @classmethod
    async def get(cls, user_id: UUID) -> str | None:
        redis = await RedisConnection.get_client()
        return await redis.get(cls._key(user_id))

    @classmethod
    async def delete(cls,user_id: UUID,) -> None:
        redis = await RedisConnection.get_client()
        await redis.delete(cls._key(user_id))

    @classmethod
    async def create(cls, user_id: UUID) -> str:
        code = _generate_verification_code()

        await cls.set(user_id, code)
        await cls.set_cooldown(user_id)

        return code