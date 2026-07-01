from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, ExpiredSignatureError, jwt

from app.core.config import settings
from app.modules.auth.schemas import AccessTokenPayload


class JWTService:
    secret_key = settings.security.jwt_secret
    algorithm = settings.security.algorithm
    expire_minutes = settings.security.access_token_expire_min

    @classmethod
    def create_access_token(cls, public_id: UUID) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(public_id),
            "iat": now,
            "exp": now + timedelta(minutes=cls.expire_minutes),
        }

        return jwt.encode(
            claims=payload,
            key=cls.secret_key,
            algorithm=cls.algorithm,
        )

    @classmethod
    def decode_access_token(cls, token: str) -> AccessTokenPayload:
        try:
            payload = jwt.decode(token, key=cls.secret_key, algorithms=[cls.algorithm])
            return AccessTokenPayload.model_validate(payload)

        except ExpiredSignatureError:
            raise ValueError("Token expired")

        except JWTError:
            raise ValueError("Invalid token")