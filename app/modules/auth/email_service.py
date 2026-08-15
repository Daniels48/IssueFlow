from app.modules.auth.cache import VerifyEmailCache, PasswordResetCache
from app.workers.celery.service import BaseEmailService


class VerifyEmailService(BaseEmailService):
    TEMPLATE = "verify_email.html"
    CACHE = VerifyEmailCache


class PasswordResetService(BaseEmailService):
    TEMPLATE = "reset_password.html"
    CACHE = PasswordResetCache