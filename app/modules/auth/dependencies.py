from typing import Annotated

from fastapi import Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.infrastructure.db.database import get_db
from app.infrastructure.db.models import User
from app.infrastructure.reddis.session_cache import SessionCache
from app.modules.auth.cookie import REFRESH_COOKIE, ACCESS_COOKIE
from app.modules.auth.jwt import JWTService
from app.modules.auth.repository import SessionRepository
from app.modules.auth.schemas import AccessTokenPayload
from app.modules.users.repository import UserRepository
from app.utils.func_utils import get_now_dt

DBSession = Annotated[AsyncSession, Depends(get_db)]

RefreshToken = Annotated[str | None, Cookie(alias=REFRESH_COOKIE)]
AccessToken = Annotated[str | None, Cookie(alias=ACCESS_COOKIE)]


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

async def get_current_user(payload: PayloadVerifySession, db: DBSession) -> User:
    user = await UserRepository.get_by_public_id(db, payload.sub)

    if not user:
        raise AppException(code=ErrorCode.USER_NOT_FOUND, message="USER not found")

    return user

CurrentUser = Annotated[User, Depends(get_current_user)]