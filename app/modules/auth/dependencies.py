from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_db
from app.infrastructure.db.models import User
from app.modules.auth.jwt import JWTService
from app.modules.users.repository import UserRepository

DBSession = Annotated[AsyncSession, Depends(get_db)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: DBSession = None) -> User:
    payload = JWTService.decode_access_token(token)

    user = await UserRepository.get_by_public_id(db,payload.sub)

    if not user:
        raise ValueError("User not found")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

