from uuid import UUID

from fastapi import APIRouter, Response, status

from app.modules.auth.cookie import AuthCookie
from app.modules.auth.dependencies import CurrentUser, ValidRefreshToken, AuthServiceDep, CurrentAuthDep
from app.modules.users.schema import UserResponse
import app.modules.auth.schema as schema

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: schema.UserCreate, service: AuthServiceDep, response: Response):
    result = await service.register(data)
    AuthCookie.set_access(response, result.tokens.access_token)
    AuthCookie.set_refresh(response, result.tokens.refresh_token)
    return result.user


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(data: schema.LoginRequest, service: AuthServiceDep, response: Response):
    tokens = await service.login(username=data.username,password=data.password)
    AuthCookie.set_access(response, tokens.access_token)
    AuthCookie.set_refresh(response, tokens.refresh_token)


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh(token_refresh: ValidRefreshToken, service: AuthServiceDep, response: Response):
    token_access = await service.refresh(refresh_token=token_refresh)
    AuthCookie.set_access(response, token_access)


@router.post("/logout",status_code=status.HTTP_204_NO_CONTENT)
async def logout(auth: CurrentAuthDep, service: AuthServiceDep, response: Response):
    await service.logout_current(user=auth.user, session_id=auth.payload.sid)
    AuthCookie.clear(response)


@router.delete("/sessions/others",status_code=status.HTTP_204_NO_CONTENT)
async def revoke_other_sessions(auth: CurrentAuthDep, service: AuthServiceDep):
    await service.revoke_other_sessions(user=auth.user, session_id=auth.payload.sid)


@router.delete("/sessions/{session_id}",status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(session_id: UUID, user: CurrentUser, service: AuthServiceDep):
    await service.revoke_session(session_id=session_id, user=user)


@router.get("/sessions",response_model=list[schema.SessionModel])
async def get_all_session(auth: CurrentAuthDep, service: AuthServiceDep):
    return await service.get_all_session(user=auth.user, session_id=auth.payload.sid)


@router.post("/password-change",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(data: schema.ChangePasswordRequest, auth: CurrentAuthDep, service: AuthServiceDep):
    await service.change_password(user=auth.user, data=data, session_id=auth.payload.sid)


@router.post("/verify-email",status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(data: schema.VerifyEmailRequest, user: CurrentUser, service: AuthServiceDep):
    await service.verify_email(user=user, code=data.code)


@router.post("/resend-email-code",status_code=status.HTTP_204_NO_CONTENT)
async def resend_email_code(user: CurrentUser, service: AuthServiceDep):
    await service.resend_verification_email(user=user)


@router.patch("/email-change")
async def email_change(new_email: schema.ChangeEmailRequest, current_user: CurrentUser, service: AuthServiceDep):
    await service.change_email(email=new_email.email, user=current_user)


@router.post("/forgot-password/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(data: schema.PasswordForgotRequest, service: AuthServiceDep):
    await service.request_password_reset(data.email)


@router.post("/forgot-password/verify", response_model=schema.ResetPasswordVerifyResponse)
async def verify_reset_code(data: schema.PasswordResetVerifyRequest, service: AuthServiceDep):
    return await service.verify_reset_code(email=data.email, code=data.code)


# @router.post("/password-reset",status_code=status.HTTP_204_NO_CONTENT)
# async def reset_password(data: ChangePasswordRequest, user: CurrentUser, service: UserService):
#     await service.reset_password(user=user, password=data.password)
#
#
# @router.post("/password-reset-code",status_code=status.HTTP_204_NO_CONTENT)
# async def send_password_reset_code(data: ChangePasswordRequest, user: CurrentUser, service: UserService):
#     await service.reset_password(user=user, password=data.password)