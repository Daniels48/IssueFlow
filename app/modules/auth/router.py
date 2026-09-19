from uuid import UUID

from fastapi import APIRouter, Response, Request, status

from app.modules.auth.cookie import AuthCookie
from app.modules.auth.dependencies import CurrentUser, ValidRefreshToken, AuthServiceDep, CurrentAuthDep
from app.modules.users.schema import UserResponse
import app.modules.auth.schema as schema

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: schema.UserCreate, service: AuthServiceDep, response: Response, request: Request):
    result = await service.register(request=request, data=data)
    AuthCookie.set_access(response, result.tokens.access_token)
    AuthCookie.set_refresh(response, result.tokens.refresh_token)
    return result.user


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(data: schema.LoginRequest, service: AuthServiceDep, response: Response, request: Request):
    tokens = await service.login(username=data.username,password=data.password, request=request)
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


@router.post("/email/verify",status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(data: schema.VerifyEmailRequest, user: CurrentUser, service: AuthServiceDep):
    await service.verify_email(user=user, code=data.code)


@router.post("/email/resend-code",status_code=status.HTTP_204_NO_CONTENT)
async def resend_email_code(user: CurrentUser, service: AuthServiceDep):
    await service.resend_verification_email(user=user)


@router.patch("/email/change", status_code=status.HTTP_204_NO_CONTENT)
async def email_change(new_email: schema.ChangeEmailRequest, current_user: CurrentUser, service: AuthServiceDep):
    await service.change_email(email=new_email.email, user=current_user)


@router.post("/forgot-password/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(data: schema.PasswordForgotRequest, service: AuthServiceDep):
    await service.request_password_reset(data.email)


@router.post("/forgot-password/verify", response_model=schema.PasswordForgotVerifyResponse)
async def verify_reset_code(data: schema.PasswordForgotVerifyRequest, service: AuthServiceDep):
    return await service.verify_reset_code(email=data.email, code=data.code)


@router.post("/forgot-password/reset",status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(data: schema.PasswordForgotResetRequest, service: AuthServiceDep):
    await service.reset_password(reset_token=data.reset_token, new_password=data.new_password)