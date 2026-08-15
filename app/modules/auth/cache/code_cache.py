from app.core.config import settings
from app.modules.auth.cache.base_code_cache import BaseCodeCache


class VerifyEmailCache(BaseCodeCache):
    PREFIX = f"{settings.redis.prefix}:verify_email"
    COOLDOWN_PREFIX = f"{settings.redis.prefix}:verify_email_cooldown"


class PasswordResetCache(BaseCodeCache):
    PREFIX = f"{settings.redis.prefix}:password_reset"
    COOLDOWN_PREFIX = f"{settings.redis.prefix}:password_reset_cooldown"


