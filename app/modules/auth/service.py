from datetime import timedelta
from typing import Any

from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions.base import AppException
from app.core.exceptions.codes import ErrorCode
from app.events import UserLoggedInEvent, UserLoggedOutEvent, UserRegisteredEvent, UserLoggedOutAllEvent
from app.infrastructure.db.models import User
from app.infrastructure.db.models.model_session import Session
from app.infrastructure.rabbitmq import RabbitPublisher
from app.infrastructure.reddis.session_cache import SessionCache
from app.modules.auth.cookie import ACCESS_COOKIE, REFRESH_COOKIE
from app.modules.auth.jwt import JWTService
from app.modules.auth.password import PasswordService
from app.modules.auth.repository import SessionRepository
from app.modules.auth.schemas import SessionModel
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate
from app.utils.func_utils import get_now_dt
from app.workers import send_email_task


SESSION_LIST_ADAPTER = TypeAdapter(list[SessionModel])

class AuthService:
    def __init__(self, repository: UserRepository, db: AsyncSession):
        self.repository = repository
        self.db = db

    async def _create_session_and_tokens(self, user: User) -> tuple[dict[str, str], Session]:
        now = get_now_dt()
        refresh_token = JWTService.generate_refresh_token()
        refresh_hash = JWTService.hash_refresh_token(refresh_token)
        time_expired = now + timedelta(days=settings.security.refresh_token_expire_days)

        session = Session(user_id=user.id, refresh_token_hash=refresh_hash, expires_at=time_expired, created_at=now)
        session = await SessionRepository.create(self.db, session)

        await SessionCache.set(session.public_id)

        access_token = JWTService.create_access_token(user.public_id, session.public_id ,now)

        return {ACCESS_COOKIE: access_token, REFRESH_COOKIE: refresh_token}, session

    async def register(self, data: UserCreate) -> dict[str, Any]:
        if await self.repository.get_by_email(self.db, data.email):
            raise AppException(ErrorCode.EMAIL_ALREADY_EXISTS,"EMAIL already exists")

        if await self.repository.get_by_username(self.db, data.username):
            raise AppException(ErrorCode.USERNAME_TAKEN,"USERNAME already exists")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=PasswordService.hash_password(data.password)
        )

        user = await self.repository.create(db=self.db, user=user)

        data_access, session = await self._create_session_and_tokens(user)

        await self.db.commit()

        # await EmailVerificationService.send(user)
        
        await RabbitPublisher.publish(UserRegisteredEvent.from_models(author=user, session=session))

        return {"user": user, "data": data_access}

    async def login(self, username: str, password: str) -> dict[str, str]:
        user = await self.repository.get_by_username(self.db, username)

        if not user:
            raise AppException(ErrorCode.USERNAME_NOT_FOUND, "Username not found")

        if not PasswordService.verify_password(password, user.password_hash):
            raise AppException(ErrorCode.PASSWORD_INVALID, "Password invalid")

        data_access, session = await self._create_session_and_tokens(user)

        await self.db.commit()

        await RabbitPublisher.publish(UserLoggedInEvent.from_models(author=user, session=session))

        # send_email_task.delay(user.email, "Welcome to IssueFlow", f"Hello {user.username}")

        return {ACCESS_COOKIE: data_access[ACCESS_COOKIE], REFRESH_COOKIE: data_access[REFRESH_COOKIE]}

    async def refresh(self, refresh_token: str) -> str:
        refresh_hash = JWTService.hash_refresh_token(refresh_token)
        session = await SessionRepository.get_by_refresh_hash(self.db, refresh_hash)

        now = get_now_dt()

        if not session :
            raise AppException(ErrorCode.SESSION_NOT_FOUND, "Session not found")

        if session.deleted_at is not None:
            raise AppException(ErrorCode.SESSION_REVOKED, "Session revoked")

        if session.expires_at < now:
            raise AppException(ErrorCode.SESSION_EXPIRED, "Session expired")

        user = await self.repository.get_by_id(self.db, session.user_id)

        if not user:
            raise AppException(ErrorCode.USER_NOT_FOUND, "User not found")
        if not user.is_active:
            raise AppException(ErrorCode.USER_NOT_ACTIVE, "User not active")

        session.updated_at = now
        await self.db.commit()

        return JWTService.create_access_token(public_id=user.public_id, session_id=session.public_id, now=now)

    async def logout_current(self, refresh_token: str, user: User) -> None:
        refresh_hash = JWTService.hash_refresh_token(refresh_token)
        session = await SessionRepository.get_by_refresh_hash(self.db, refresh_hash)
        await SessionRepository.delete(db=self.db, session=session)
        await SessionCache.delete(session.public_id)

        await RabbitPublisher.publish(UserLoggedOutEvent.from_models(author=user, session=session))

    async def logout_device_id(self, refresh_token: str, user: User) -> None:
        pass
        # refresh_hash = JWTService.hash_refresh_token(refresh_token)
        # session = await SessionRepository.get_by_refresh_hash(self.db, refresh_hash)
        # await SessionRepository.delete(db=self.db, session=session)
        #
        # await RabbitPublisher.publish(UserLoggedOutEvent.from_models(author=user, session=session))

    async def logout_all(self, refresh_token: str, user: User) -> None:
        pass
        # refresh_hash = JWTService.hash_refresh_token(refresh_token)
        # session = await SessionRepository.get_by_refresh_hash(self.db, refresh_hash)
        # await SessionRepository.delete(db=self.db, session=session)
        #
        # await RabbitPublisher.publish(UserLoggedOutAllEvent.from_models(author=user, session=session))

    async def get_all_session(self, user: User) -> list[SessionModel]:
        session_list = await SessionRepository.get_list_by_user_id(db=self.db, user_id=user.id)
        return SESSION_LIST_ADAPTER.validate_python(session_list)