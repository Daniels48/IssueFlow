import hashlib
import hmac
import secrets
from datetime import timedelta, datetime
from uuid import UUID

from jose import JWTError, ExpiredSignatureError, jwt

from app.core.config import settings
from app.modules.auth.schemas import AccessTokenPayload


class JWTService:
    secret_key = settings.security.jwt_secret
    refresh_key = settings.security.refresh_secret
    algorithm = settings.security.algorithm
    expire_minutes = settings.security.access_token_expire_min

    @classmethod
    def create_access_token(cls, public_id: UUID, now: datetime) -> str:

        payload = {
            "sub": str(public_id),
            "iat": now,
            "exp": now + timedelta(minutes=cls.expire_minutes),
        }

        return jwt.encode(claims=payload, key=cls.secret_key, algorithm=cls.algorithm)

    @classmethod
    def decode_access_token(cls, token: str) -> AccessTokenPayload:
        try:
            payload = jwt.decode(token, key=cls.secret_key, algorithms=[cls.algorithm])
            return AccessTokenPayload.model_validate(payload)

        except ExpiredSignatureError:
            raise ValueError("Token expired")

        except JWTError:
            raise ValueError("Invalid token")

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        return hmac.new(settings.security.refresh_secret.encode(), token.encode(), hashlib.sha256).hexdigest()

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(64)