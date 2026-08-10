import hashlib
import hmac
import secrets
from datetime import timedelta, datetime
from uuid import UUID

from jose import JWTError, ExpiredSignatureError, jwt
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import AppException, ErrorCode
from app.modules.auth.schemas import AccessTokenPayload


class JWTService:
    secret_key = settings.security.jwt_secret
    refresh_key = settings.security.refresh_secret
    algorithm = settings.security.algorithm
    expire_minutes = settings.security.access_token_expire_min

    @classmethod
    def create_access_token(cls, public_id: UUID, session_id: UUID, now: datetime) -> str:

        payload = {
            "sub": str(public_id),
            "iat": now,
            "sid": str(session_id),
            "exp": now + timedelta(minutes=cls.expire_minutes),
        }

        return jwt.encode(claims=payload, key=cls.secret_key, algorithm=cls.algorithm)

    @classmethod
    def decode_access_token(cls, token: str) -> AccessTokenPayload:
        try:
            payload = jwt.decode(token, key=cls.secret_key, algorithms=[cls.algorithm])
            return AccessTokenPayload.model_validate(payload)

        except ExpiredSignatureError:
            raise AppException(code=ErrorCode.TOKEN_EXPIRED, message="Token expired")

        except JWTError as exc:
            raise AppException(code=ErrorCode.INVALID_TOKEN, message=f"Invalid access token: {exc}") from exc

        except ValidationError as exc:
            raise AppException(code=ErrorCode.INVALID_TOKEN,message=f"Invalid access token payload: {exc}") from exc

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        return hmac.new(settings.security.refresh_secret.encode(), token.encode(), hashlib.sha256).hexdigest()

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(64)