from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.db.models import User
from app.infrastructure.db.models.model_session import Session
from app.modules.auth.cookie import ACCESS_COOKIE, REFRESH_COOKIE
from app.modules.auth.jwt import JWTService
from app.modules.auth.password import PasswordService
from app.modules.auth.repository import SessionRepository
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate
from app.utils.func_utils import get_now_dt


class AuthService:
    def __init__(self, repository: UserRepository, db: AsyncSession):
        self.repository = repository
        self.db = db

    async def register(self, data: UserCreate) -> User:
        if await self.repository.get_by_email(self.db, data.email):
            raise ValueError("Email already exists")

        if await self.repository.get_by_username(self.db, data.username):
            raise ValueError("Username already exists")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=PasswordService.hash_password(data.password)
        )

        user = await self.repository.create(db=self.db, user=user)

        await self.db.commit()

        return user

    async def login(self, username: str, password: str) -> dict[str, str]:
        user = await self.repository.get_by_username(self.db, username)

        if not user:
            raise ValueError("Invalid credentials")

        if not PasswordService.verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        access_token = JWTService.create_access_token(user.public_id, get_now_dt())

        refresh_token = JWTService.generate_refresh_token()
        refresh_hash = JWTService.hash_refresh_token(refresh_token)
        time_expired = get_now_dt() + timedelta(days=settings.security.refresh_token_expire_days)

        session = Session(user_id=user.id, refresh_token_hash=refresh_hash, expires_at=time_expired)

        await SessionRepository.create(self.db, session)

        return {ACCESS_COOKIE: access_token, REFRESH_COOKIE: refresh_token}

    async def refresh(self, refresh_token: str) -> str:
        refresh_hash = JWTService.hash_refresh_token(refresh_token)
        session = await SessionRepository.get_by_refresh_hash(self.db, refresh_hash)

        now = get_now_dt()

        if not session or session.expires_at < now or session.deleted_at is not None:
            raise HTTPException(status_code=403)

        user = await self.repository.get_by_id(self.db, session.user_id)

        if not user or not user.is_active:
            raise HTTPException(status_code=401)

        try:
            session.updated_at = now
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise HTTPException(status_code=500)

        access_token = JWTService.create_access_token(public_id=user.public_id, now=now)

        return access_token
