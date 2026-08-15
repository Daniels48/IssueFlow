from dataclasses import dataclass

from app.infrastructure.db.models import Session, User


@dataclass(frozen=True, slots=True)
class CookieConfig:
    path: str
    max_age: int

@dataclass(frozen=True, slots=True)
class AuthTokens:
    access_token: str
    refresh_token: str


@dataclass(frozen=True, slots=True)
class AuthResult:
    user: User
    tokens: AuthTokens


@dataclass(frozen=True, slots=True)
class AuthSessionResult:
    tokens: AuthTokens
    session: Session