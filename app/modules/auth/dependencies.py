from typing import Annotated

from fastapi import Depends, Cookie, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_db
from app.infrastructure.db.models import User
from app.modules.auth.cookie import REFRESH_COOKIE
from app.modules.auth.jwt import JWTService
from app.modules.auth.schemas import AccessTokenPayload
from app.modules.users.repository import UserRepository

DBSession = Annotated[AsyncSession, Depends(get_db)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

RefreshToken = Annotated[str | None, Cookie(alias=REFRESH_COOKIE)]


def get_refresh_token(refresh_token: RefreshToken) -> str:
    if refresh_token is None:
        raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED,detail="Refresh token missing")

    return refresh_token


async def get_current_payload(access_token: str | None = Cookie(default=None)) -> AccessTokenPayload:
    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not authenticated")

    return JWTService.decode_access_token(access_token)


CurrentPayload = Annotated[AccessTokenPayload, Depends(get_current_payload)]

async def get_current_user(payload: CurrentPayload, db: DBSession) -> User:
    user = await UserRepository.get_by_public_id(db, payload.sub)

    if not user:
        raise ValueError("User not found")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

