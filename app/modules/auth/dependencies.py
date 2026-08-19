from typing import Annotated
from dataclasses import dataclass

from fastapi import Depends, Cookie, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.infrastructure.db.database import get_db
from app.infrastructure.db.models import User
from app.modules.auth.cache import SessionCache
from app.modules.auth.cookie import AuthCookie
from app.modules.auth.jwt import JWTService
from app.modules.auth.repository import SessionRepository
from app.modules.auth.schema import AccessTokenPayload
from app.modules.auth.service import AuthService
from app.modules.users.repository import UserRepository
from app.utils.func_utils import get_now_dt

DBSession = Annotated[AsyncSession, Depends(get_db)]

RefreshToken = Annotated[str | None, Cookie(alias=AuthCookie.REFRESH)]
AccessToken = Annotated[str | None, Cookie(alias=AuthCookie.ACCESS)]


def get_auth_service(db: DBSession) -> AuthService:
    return AuthService(db=db)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

def get_refresh_token(refresh_token: RefreshToken = None) -> str:
    if refresh_token is None:
        raise AppException(code=ErrorCode.REFRESH_TOKEN_NOT_FOUND, message="Refresh token not found")

    return refresh_token

ValidRefreshToken = Annotated[str, Depends(get_refresh_token)]


async def get_current_payload(access_token: AccessToken = None) -> AccessTokenPayload:
    if access_token is None:
        raise AppException(code=ErrorCode.UNAUTHORIZED, message="Not access token")

    return JWTService.decode_access_token(access_token)

CurrentPayload = Annotated[AccessTokenPayload, Depends(get_current_payload)]


async def verify_session(payload: CurrentPayload, db: DBSession):
    session_redis = await SessionCache.exists(session_id=payload.sid)

    if not session_redis:
        session_db = await SessionRepository.get_by_session_id(db=db, session_id=payload.sid)

        if not session_db:
            # logger.warning("Session not found", extra={"event": "session_not_found"})
            raise AppException(code=ErrorCode.SESSION_NOT_FOUND, message="Session not found")

        if session_db.deleted_at is not None:
            # logger.warning("Session revoked", extra={"event": "session_revoked"})
            raise AppException(code=ErrorCode.SESSION_REVOKED, message="Session revoked")

        if session_db.expires_at < get_now_dt():
            raise AppException(code=ErrorCode.SESSION_EXPIRED, message="Session expired")

        await SessionCache.set(session_id=payload.sid)

    return payload

PayloadVerifySession = Annotated[AccessTokenPayload, Depends(verify_session)]

async def get_current_user(payload: PayloadVerifySession, db: DBSession, request: Request) -> User:
    user = await UserRepository.get_by_public_id(db, payload.sub)
    request.state.user_id = str(user.public_id)

    if not user:
        raise AppException(code=ErrorCode.USER_NOT_FOUND, message="User not found")

    if not user.is_active:
        raise AppException(code=ErrorCode.USER_NOT_ACTIVE, message="User not active")

    return user

CurrentUser = Annotated[User, Depends(get_current_user)]


@dataclass(frozen=True)
class CurrentAuth:
    user: User
    payload: AccessTokenPayload

async def get_current_auth(payload: PayloadVerifySession, db: DBSession, request: Request) -> CurrentAuth:
    user = await get_current_user(payload, db, request)
    return CurrentAuth(user=user, payload=payload)


CurrentAuthDep = Annotated[CurrentAuth,Depends(get_current_auth)]