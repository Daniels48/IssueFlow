from datetime import timedelta, datetime
from uuid import UUID

from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException, ErrorCode
from app.events import UserLoggedInEvent, UserLoggedOutEvent, UserRegisteredEvent, UserLoggedOutAllEvent, \
    UserPasswordChangedEvent
from app.infrastructure.db.models import User, Session
from app.infrastructure.rabbitmq import RabbitPublisher
from app.modules.auth.dto import AuthSessionResult, AuthResult, AuthTokens
from app.modules.auth.email_service import VerifyEmailService, PasswordResetService
from app.modules.auth.jwt import JWTService
from app.modules.auth.password import PasswordService
from app.modules.auth.repository import SessionRepository
from app.modules.auth.cache import PasswordResetTokenCache, VerifyEmailCache, PasswordResetCache, SessionCache
from app.modules.users.repository import UserRepository
from app.modules.auth.schema import UserCreate, ChangePasswordRequest, SessionModel, ResetPasswordVerifyResponse
from app.utils.func_utils import get_now_dt


SESSION_LIST_ADAPTER = TypeAdapter(list[SessionModel])


def _check_valid_session(session: Session | None, now: datetime) -> Session | None:
    if not session :
        raise AppException(ErrorCode.SESSION_NOT_FOUND, "Session not found")

    if session.deleted_at is not None:
        raise AppException(ErrorCode.SESSION_REVOKED, "Session revoked")

    if session.expires_at < now:
        raise AppException(ErrorCode.SESSION_EXPIRED, "Session expired")

    return session


def _check_valid_user(user: User | None) -> User | None:
    if not user:
        raise AppException(ErrorCode.USER_NOT_FOUND, "User not found")

    if not user.is_active:
        raise AppException(ErrorCode.USER_NOT_ACTIVE, "User not active")

    return user


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository()
        self.db = db

    async def _create_session_and_tokens(self, user: User, now: datetime) -> AuthSessionResult:
        refresh_token = JWTService.generate_refresh_token()

        session = Session(
            user_id=user.id,
            refresh_token_hash=JWTService.hash_refresh_token(refresh_token),
            expires_at=now + timedelta(days=settings.security.refresh_token_expire_days),
            created_at=now
        )

        session = await SessionRepository.create(self.db, session)

        await SessionCache.set(session.public_id)

        tokens = AuthTokens(
            access_token=JWTService.create_access_token(user.public_id, session.public_id ,now),
            refresh_token=refresh_token
        )

        return AuthSessionResult(tokens=tokens, session=session)

    async def register(self, data: UserCreate) -> AuthResult:
        if await self.repository.get_by_email(self.db, data.email):
            raise AppException(ErrorCode.EMAIL_ALREADY_EXISTS,"EMAIL already exists")

        if await self.repository.get_by_username(self.db, data.username):
            raise AppException(ErrorCode.USERNAME_TAKEN,"USERNAME already exists")

        now = get_now_dt()

        user = User(
            username=data.username,
            email=data.email,
            password_hash=PasswordService.hash_password(data.password),
            created_at=now
        )

        user = await self.repository.create(db=self.db, user=user)

        result = await self._create_session_and_tokens(user, now)

        await self.db.commit()

        await VerifyEmailService.send(user)
        
        await RabbitPublisher.publish(UserRegisteredEvent.from_models(author=user, session=result.session))

        return AuthResult(user=user, tokens=result.tokens)

    async def login(self, username: str, password: str) -> AuthTokens:
        user = await self.repository.get_by_username(self.db, username)

        if not user:
            raise AppException(ErrorCode.USERNAME_NOT_FOUND, "Username not found")

        if not PasswordService.verify_password(password, user.password_hash):
            raise AppException(ErrorCode.PASSWORD_INVALID, "Password invalid")

        now = get_now_dt()

        result = await self._create_session_and_tokens(user, now)

        await self.db.commit()

        await RabbitPublisher.publish(UserLoggedInEvent.from_models(author=user, session=result.session))

        return result.tokens

    async def refresh(self, refresh_token: str) -> str:
        refresh_hash = JWTService.hash_refresh_token(refresh_token)
        session = await SessionRepository.get_by_refresh_hash(self.db, refresh_hash)

        now = get_now_dt()

        session = _check_valid_session(session, now)

        user = await self.repository.get_by_id(self.db, session.user_id)
        user = _check_valid_user(user)

        session.updated_at = now
        await self.db.commit()

        return JWTService.create_access_token(public_id=user.public_id, session_id=session.public_id, now=now)

    async def logout_current(self, session_id: UUID, user: User) -> None:
        session = await SessionRepository.get_by_session_id(self.db, session_id)
        now = get_now_dt()
        session = _check_valid_session(session, now)

        session.deleted_at = now
        await self.db.commit()

        await SessionCache.delete(session.public_id)

        await RabbitPublisher.publish(UserLoggedOutEvent.from_models(author=user, session=session))

    async def revoke_session(self,session_id: UUID, user: User) -> None:
        session = await SessionRepository.get_by_session_id(db=self.db,session_id=session_id)
        now = get_now_dt()
        session = _check_valid_session(session, now)

        if session.user_id != user.id:
            # forbidden
            raise AppException(code=ErrorCode.SESSION_NOT_FOUND,message="Session not found")

        session.deleted_at = now
        await self.db.commit()

        await SessionCache.delete(session.public_id)

        await RabbitPublisher.publish(UserLoggedOutEvent.from_models(author=user, session=session))

    async def _revoke_other_sessions(self, user: User, session_id: UUID) -> list[Session]:
        now = get_now_dt()
        sessions = await SessionRepository.get_list_active_by_user_id(db=self.db, user_id=user.id, now=now)

        for session in sessions:
            if session.public_id == session_id:
                continue

            session.deleted_at = now
            await SessionCache.delete(session.public_id)

        return sessions

    async def _revoke_all_sessions(self, user_id: int) -> None:
        now = get_now_dt()

        sessions = await SessionRepository.get_list_active_by_user_id(db=self.db, user_id=user_id, now=now)

        for session in sessions:
            session.deleted_at = now

        for session in sessions:
            await SessionCache.delete(session.public_id)

    async def revoke_other_sessions(self, user: User, session_id: UUID) -> None:
        sessions = await self._revoke_other_sessions(user, session_id)
        await self.db.commit()

        # await RabbitPublisher.publish(UserLoggedOutAllEvent.from_models(author=user,session=sessions[0]))

    async def get_all_session(self, user: User, session_id: UUID) -> list[SessionModel]:
        now = get_now_dt()
        session_list = await SessionRepository.get_list_active_by_user_id(db=self.db, user_id=user.id, now=now)
        list_return = SESSION_LIST_ADAPTER.validate_python(session_list)

        for item in list_return:
            if item.public_id == session_id:
                item.is_current = True

        return list_return

    async def change_password(self, data: ChangePasswordRequest, user: User, session_id: UUID):
        if not PasswordService.verify_password(data.old_password, user.password_hash):
            raise AppException(ErrorCode.PASSWORD_INVALID, "Password invalid")

        if PasswordService.verify_password(data.new_password, user.password_hash):
            raise AppException(ErrorCode.NEW_PASSWORD_SAME, "New password must be different")

        user.password_hash = PasswordService.hash_password(data.new_password)
        sessions = await self._revoke_other_sessions(user, session_id)
        await self.db.commit()

        # await RabbitPublisher.publish(UserPasswordChangedEvent.from_models(author=user, session=sessions[0]))

    async def verify_email(self, user: User, code: str) -> None:
        if user.email_verified_at:
            raise AppException(ErrorCode.EMAIL_VERIFIED_ALREADY, "Email already verified")

        if not await VerifyEmailCache.verify(user.public_id, code):
            raise AppException(ErrorCode.INVALID_EMAIL_VERIFY_CODE, "Invalid email code")

        user.email_verified_at = get_now_dt()

        await VerifyEmailCache.delete(user.public_id)

        await self.db.commit()

    @staticmethod
    async def resend_verification_email(user: User):
        if user.email_verified_at:
            raise AppException(ErrorCode.EMAIL_VERIFIED_ALREADY, "Email already verified")

        await VerifyEmailService.send(user)

    async def change_email___________________________(self, user: User, email: str) -> None:
        if user.email == email:
            raise AppException(ErrorCode.NEW_EMAIL_SAME, "New email must be different")

        if await self.repository.get_by_email(self.db, email):
            raise AppException(ErrorCode.EMAIL_ALREADY_EXISTS, "Email already exists")

        user.email = email
        user.email_verified_at = None

        await self.db.commit()

        await VerifyEmailService.send(user)

    async def request_password_reset(self, email: str) -> None:
        user = await self.repository.get_by_email(self.db, email)

        if not user:
            return

        await PasswordResetService.send(user)

    async def verify_reset_code(self, email: str, code: str) -> ResetPasswordVerifyResponse:
        user = await self.repository.get_by_email(self.db, email)

        if not user or not await PasswordResetCache.verify(user.public_id, code):
            raise AppException(ErrorCode.INVALID_PASSWORD_RESET_CODE,"Invalid reset code")

        reset_token = PasswordResetTokenCache.generate()

        await PasswordResetTokenCache.set(reset_token, user.public_id)

        await PasswordResetCache.delete(user.public_id)

        return ResetPasswordVerifyResponse(reset_token=reset_token)

    async def reset_password(self, reset_token: str, new_password: str) -> None:
        user_id = await PasswordResetTokenCache.get_user_id(reset_token)

        if user_id is None:
            raise AppException(ErrorCode.INVALID_PASSWORD_RESET_TOKEN,"Invalid password reset token")

        user = await self.repository.get_by_public_id(self.db, user_id)
        user = _check_valid_user(user)

        if PasswordService.verify_password(new_password, user.password_hash):
            raise AppException(ErrorCode.NEW_PASSWORD_SAME,"New password must be different",)

        user.password_hash = PasswordService.hash_password(new_password)

        await self._revoke_all_sessions(user_id=user.id)

        await self.db.commit()

        await PasswordResetTokenCache.delete(reset_token)