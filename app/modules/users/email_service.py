from app.core.config import settings
from app.infrastructure.reddis.base_cache import BaseCodeCache
from app.workers.celery.service import BaseEmailService


class VerifyEmailCache(BaseCodeCache):
    PREFIX = f"{settings.redis.prefix}:verify_email"
    COOLDOWN_PREFIX = f"{settings.redis.prefix}:verify_email_cooldown"


class PasswordResetCache(BaseCodeCache):
    PREFIX = f"{settings.redis.prefix}:password_reset"
    COOLDOWN_PREFIX = f"{settings.redis.prefix}:password_reset_cooldown"


class VerifyEmailService(BaseEmailService):
    TEMPLATE = "verify_email.html"
    CACHE = VerifyEmailCache

class PasswordResetService(BaseEmailService):
    TEMPLATE = "reset_password.html"
    CACHE = PasswordResetCache