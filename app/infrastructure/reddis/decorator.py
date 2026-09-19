from functools import wraps
from redis.exceptions import RedisError

from app.core.exceptions import CacheUnavailableError


def handle_redis_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RedisError as exc:
            raise CacheUnavailableError from exc

    return wrapper