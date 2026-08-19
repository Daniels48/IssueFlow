import hashlib
import hmac
import secrets
from uuid import UUID

from app.core.config import settings
from app.infrastructure.reddis.connection import RedisConnection


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

    @staticmethod
    def _hash_code(code: str) -> str:
        code_hash = settings.security.code_hash_secret
        return hmac.new(code_hash.encode(), code.encode(), hashlib.sha256).hexdigest()

    @classmethod
    async def set(cls, user_id: UUID, code: str) -> None:
        redis = await RedisConnection.get_client()

        await redis.set(cls._key(user_id), cls._hash_code(code), ex=cls.TTL)

    @classmethod
    async def verify(cls, user_id: UUID, code: str) -> bool:
        redis = await RedisConnection.get_client()

        saved_hash = await redis.get(cls._key(user_id))

        if saved_hash is None:
            return False

        code_hash = cls._hash_code(code)

        return hmac.compare_digest(saved_hash, code_hash)

    @classmethod
    async def delete(cls, user_id: UUID) -> None:
        redis = await RedisConnection.get_client()
        await redis.delete(cls._key(user_id))

    @staticmethod
    def _generate_verification_code() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @classmethod
    async def create(cls, user_id: UUID) -> str:
        code = cls._generate_verification_code()

        await cls.set(user_id, code)

        return code