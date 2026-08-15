import hashlib
import secrets
from uuid import UUID

from app.core.config import settings
from app.infrastructure.reddis.connection import RedisConnection


class PasswordResetTokenCache:
    PREFIX = f"{settings.redis.prefix}:password_reset_token"
    TTL = 300  # 5 минут

    @classmethod
    def _key(cls, token_hash: str) -> str:
        return f"{cls.PREFIX}:{token_hash}"

    @staticmethod
    def _hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def generate() -> str:
        return secrets.token_urlsafe(64)

    @classmethod
    async def set(cls, token: str, user_id: UUID) -> None:
        redis = await RedisConnection.get_client()

        token_hash = cls._hash(token)

        await redis.set(cls._key(token_hash), str(user_id), ex=cls.TTL)

    @classmethod
    async def get_user_id(cls,token: str) -> UUID | None:
        redis = await RedisConnection.get_client()

        token_hash = cls._hash(token)

        value = await redis.get(cls._key(token_hash))

        if value is None:
            return None

        return UUID(value)

    @classmethod
    async def delete(cls,token: str) -> None:
        redis = await RedisConnection.get_client()

        token_hash = cls._hash(token)

        await redis.delete( cls._key(token_hash))