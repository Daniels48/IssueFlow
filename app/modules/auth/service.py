import logging

from fastapi import Request
from datetime import timedelta, datetime
from uuid import UUID

from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException, ErrorCode, CacheUnavailableError
from app.core.obsarvability.utils import parse_user_agent, get_client_info

from app.events.outbox import OutboxFactory
from app.events import user as user_events

from app.infrastructure.db.models import User, Session

from app.modules.auth.dto import AuthSessionResult, AuthResult, AuthTokens
from app.modules.auth.jwt import JWTService
from app.modules.auth.password import PasswordService
from app.modules.auth.repository import SessionRepository
from app.modules.auth.cache import PasswordResetTokenCache, VerifyEmailCache, PasswordResetCache, SessionCache
from app.modules.auth.schema import UserCreate, ChangePasswordRequest, SessionModel, PasswordForgotVerifyResponse

from app.modules.users.repository import UserRepository

from app.utils.func_utils import get_now_dt


logger = logging.getLogger(__name__)

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


def get_session_client_data(request: Request) -> dict:
    user_agent = request.headers.get("user-agent")

    ua = parse_user_agent(user_agent)
    ip = request.client.host

    client_info = request.headers.get("X-Client-Info")
    ci = get_client_info(client_info)

    return {**ua, **ci, "ip_address":ip}


def update_session_client_data(session: Session, request: Request) -> None:

    client_data = get_session_client_data(request)

    for field, value in client_data.items():
        setattr(session, field, value)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository()
        self.db = db

    async def _create_session_and_tokens(self, user: User, now: datetime, request: Request) -> AuthSessionResult:
        refresh_token = JWTService.generate_refresh_token()

        session = Session(
            user_id=user.id,
            refresh_token_hash=JWTService.hash_refresh_token(refresh_token),
            expires_at=now + timedelta(days=settings.security.refresh_token_expire_days),
            created_at=now
        )

        update_session_client_data(session, request)

        session = await SessionRepository.create(self.db, session)

        tokens = AuthTokens(
            access_token=JWTService.create_access_token(user.public_id, session.public_id ,now),
            refresh_token=refresh_token
        )

        return AuthSessionResult(tokens=tokens, session=session)

    async def register(self, request: Request, data: UserCreate) -> AuthResult:
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

        result = await self._create_session_and_tokens(user=user, now=now, request=request)

        event = user_events.UserRegisteredEvent.from_model(user, result.session.public_id, now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        try:
            await SessionCache.set(result.session.public_id)
        except CacheUnavailableError:
            logger.exception("Failed to set session in Redis",extra={"session_id": str(result.session.public_id)})

        return AuthResult(user=user, tokens=result.tokens)

        # await VerifyEmailService.send(user)
        # await RabbitPublisher.publish(UserRegisteredEvent.from_models(author=user, session=result.session))

    async def login(self, request: Request, username: str, password: str) -> AuthTokens:
        user = await self.repository.get_by_username(self.db, username)

        if not user:
            raise AppException(ErrorCode.USERNAME_NOT_FOUND, "Username not found")

        if not PasswordService.verify_password(password, user.password_hash):
            raise AppException(ErrorCode.PASSWORD_INVALID, "Password invalid")

        now = get_now_dt()

        result = await self._create_session_and_tokens(user, now, request)

        event = user_events.UserLoggedInEvent.from_model(user, result.session.public_id, now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        try:
            await SessionCache.set(result.session.public_id)
        except CacheUnavailableError:
            logger.exception("Failed to set session in Redis", extra={"session_id": str(result.session.public_id)})

        return result.tokens

        # await RabbitPublisher.publish(UserLoggedInEvent.from_models(author=user, session=result.session))

    async def refresh(self, refresh_token: str) -> str:
        refresh_hash = JWTService.hash_refresh_token(refresh_token)

        now = get_now_dt()

        session = await SessionRepository.get_by_refresh_hash(self.db, refresh_hash)
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

        event = user_events.UserLoggedOutEvent.from_model(user=user, session_id=session_id, occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        try:
            await SessionCache.delete(session.public_id)
        except CacheUnavailableError:
            logger.exception("Failed to del session in Redis", extra={"session_id": str(session.public_id)})

        # await RabbitPublisher.publish(UserLoggedOutEvent.from_models(author=user, session=session))

    async def revoke_session(self, session_id: UUID, user: User) -> None:
        session = await SessionRepository.get_by_session_id(db=self.db,session_id=session_id)
        now = get_now_dt()
        session = _check_valid_session(session, now)

        if session.user_id != user.id:
            raise AppException(code=ErrorCode.SESSION_NOT_FOUND,message="Session not found")

        session.deleted_at = now

        event = user_events.UserLoggedOutEvent.from_model(user=user, session_id=session_id, occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        try:
            await SessionCache.delete(session.public_id)
        except CacheUnavailableError:
            logger.exception("Failed to del session in Redis", extra={"session_id": str(session.public_id)})

        # await RabbitPublisher.publish(UserLoggedOutEvent.from_models(author=user, session=session))

    async def revoke_other_sessions(self, user: User, session_id: UUID) -> None:
        now = get_now_dt()

        sessions = await SessionRepository.get_list_active_by_user_id(db=self.db, user_id=user.id, now=now)

        session_ids = []

        for session in sessions:
            if session.public_id == session_id:
                continue

            session.deleted_at = now
            session_ids.append(session.public_id)

        event = user_events.UserLoggedOutAllEvent.from_model(user=user, occurred_at=now, session_ids=session_ids)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        for session in sessions:
            try:
                await SessionCache.delete(session.public_id)
            except CacheUnavailableError:
                logger.exception("Failed to del session in Redis", extra={"session_id": str(session.public_id)})

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

        now = get_now_dt()
        user.password_hash = PasswordService.hash_password(data.new_password)
        user.updated_at = now
        user.password_changed_at = now

        sessions = await SessionRepository.get_list_active_by_user_id(db=self.db, user_id=user.id, now=now)
        session_ids = []

        for session in sessions:
            if session.public_id == session_id:
                continue

            session.deleted_at = now
            session_ids.append(session.public_id)


        event = user_events.UserPasswordChangedEvent.from_model(user=user,occurred_at=get_now_dt(),session_ids=session_ids)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        for session in sessions:
            try:
                await SessionCache.delete(session.public_id)
            except CacheUnavailableError:
                logger.exception("Failed to del session in Redis", extra={"session_id": str(session.public_id)})

        # await RabbitPublisher.publish(UserPasswordChangedEvent.from_models(author=user, session=sessions[0]))

    async def verify_email(self, user: User, code: str) -> None:
        if user.email_verified_at:
            raise AppException( ErrorCode.EMAIL_VERIFIED_ALREADY,"Email already verified")

        try:
            valid = await VerifyEmailCache.verify(user.public_id, code)
        except CacheUnavailableError:
            logger.exception("Failed to verify email code in Redis")
            raise AppException(ErrorCode.SERVICE_UNAVAILABLE, "Email verification is temporarily unavailable")

        if not valid:
            raise AppException(ErrorCode.INVALID_EMAIL_VERIFY_CODE,"Invalid email code")

        now = get_now_dt()

        user.email_verified_at = now

        event = user_events.UserEmailVerifyEvent.from_model(user=user, occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        try:
            await VerifyEmailCache.delete(user.public_id)
        except CacheUnavailableError:
            logger.exception("Failed to delete email verification code from Redis")

    async def resend_verification_email(self, user: User):
        if user.email_verified_at:
            raise AppException(ErrorCode.EMAIL_VERIFIED_ALREADY, "Email already verified")

        event = user_events.UserEmailVerificationRequestedEvent.from_model(user=user,occurred_at=get_now_dt())
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        # await VerifyEmailService.send(user)

    async def change_email(self, user: User, email: str) -> None:
        if user.email == email:
            raise AppException(ErrorCode.NEW_EMAIL_SAME, "New email must be different")

        if await self.repository.get_by_email(self.db, email):
            raise AppException(ErrorCode.EMAIL_ALREADY_EXISTS, "Email already exists")

        now = get_now_dt()

        old_email = user.email
        user.email = email
        user.email_verified_at = None
        user.updated_at = now

        event = user_events.UserEmailChangedEvent.from_model(
            user=user,
            occurred_at=now,
            old_email=old_email,
            new_email=email
        )
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        # await VerifyEmailService.send(user)

    async def request_password_reset(self, email: str) -> None:
        user = await self.repository.get_by_email(self.db, email)

        if not user:
            return

        event = user_events.UserPasswordResetRequestedEvent.from_model(user=user, occurred_at=get_now_dt())
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        # await PasswordResetService.send(user) тут create_PasswordResetCache

    async def verify_reset_code(self, email: str, code: str) -> PasswordForgotVerifyResponse:
        user = await self.repository.get_by_email(self.db,email)

        if not user:
            raise AppException(ErrorCode.INVALID_PASSWORD_RESET_CODE,"Invalid reset code")

        try:
            valid = await PasswordResetCache.verify(user.public_id, code)
        except CacheUnavailableError:
            logger.exception("Failed verify code in Redis")
            raise AppException(ErrorCode.SERVICE_UNAVAILABLE, "Password reset is temporarily unavailable")

        if not valid:
            raise AppException(ErrorCode.INVALID_PASSWORD_RESET_CODE,"Invalid reset code")

        reset_token = PasswordResetTokenCache.generate()

        try:
            await PasswordResetTokenCache.set(reset_token, user.public_id)
        except CacheUnavailableError:
            logger.exception("Failed to create password reset token in Redis")
            raise AppException(ErrorCode.SERVICE_UNAVAILABLE,"Password reset is temporarily unavailable")

        return PasswordForgotVerifyResponse(reset_token=reset_token)

    async def reset_password(self, reset_token: str, new_password: str) -> None:
        try:
            user_id = await PasswordResetTokenCache.get_user_id(reset_token)
        except CacheUnavailableError:
            logger.exception("Failed get reset_token in Redis")
            raise AppException(ErrorCode.SERVICE_UNAVAILABLE, "Password reset is temporarily unavailable")

        if user_id is None:
            raise AppException(ErrorCode.INVALID_PASSWORD_RESET_TOKEN,"Invalid password reset token")

        user = await self.repository.get_by_public_id(self.db, user_id)
        user = _check_valid_user(user)

        if PasswordService.verify_password(new_password, user.password_hash):
            raise AppException(ErrorCode.NEW_PASSWORD_SAME,"New password must be different",)

        now = get_now_dt()

        user.password_hash = PasswordService.hash_password(new_password)
        user.updated_at = now
        user.password_changed_at = now

        sessions = await SessionRepository.get_list_active_by_user_id(db=self.db, user_id=user.id, now=now)
        session_ids = []

        for session in sessions:
            session.deleted_at = now
            session_ids.append(session.public_id)

        event = user_events.UserPasswordChangedEvent.from_model(user=user, occurred_at=now, session_ids=session_ids)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        for session in sessions:
            try:
                await SessionCache.delete(session.public_id)
            except CacheUnavailableError:
                logger.exception("Failed to delete session from Redis",extra={"session_id": str(session.public_id)})

        try:
            await PasswordResetTokenCache.delete(reset_token)
        except CacheUnavailableError:
            logger.exception("Failed to delete reset_token from Redis")

