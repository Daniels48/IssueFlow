from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_db
from app.infrastructure.db.models import User
from app.modules.auth.jwt import JWTService
from app.modules.auth.schemas import AccessTokenPayload
from app.modules.users.repository import UserRepository

DBSession = Annotated[AsyncSession, Depends(get_db)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_payload(token: str = Depends(oauth2_scheme)) -> AccessTokenPayload:
    return JWTService.decode_access_token(token)


CurrentPayload = Annotated[AccessTokenPayload, Depends(get_current_payload)]


async def get_current_user(payload: CurrentPayload, db: DBSession = None) -> User:
    user = await UserRepository.get_by_public_id(db,payload.sub)

    if not user:
        raise ValueError("User not found")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

