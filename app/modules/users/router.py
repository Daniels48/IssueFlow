from uuid import UUID

from fastapi import APIRouter, status, Response

from app.modules.auth.dependencies import CurrentUser, DBSession
from app.modules.users.schema import UserResponse, UserShortResponse, VerifyEmailRequest, ChangeEmailRequest, \
    ChangePasswordRequest
from app.modules.users.service import UserService

router = APIRouter(prefix="/users",tags=["Users"])

@router.get("/me",response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user

@router.get("/search", response_model=list[UserShortResponse])
async def search_users(query: str, project_id: UUID, current_user: CurrentUser, service: UserService):
    return await service.search_users(query=query, project_id=project_id, current_user_id=current_user.id)


@router.post("/verify-email",status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(data: VerifyEmailRequest, user: CurrentUser, service: UserService) -> Response:
    await service.verify_email(user=user, code=data.code)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    return response


@router.post("/resend-email-code",status_code=status.HTTP_204_NO_CONTENT)
async def resend_email_code(user: CurrentUser, service: UserService) -> Response:
    await service.resend_verification_email(user=user)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    return response

@router.patch("/email-change")
async def email_change(new_email: ChangeEmailRequest, current_user: CurrentUser, service: UserService):
    await service.change_email(email=new_email.email, user=current_user)


@router.post("/password-change",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(data: ChangePasswordRequest, user: CurrentUser, service: UserService) -> Response:
    await service.change_password(user=user, password=data.password)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    return response

@router.post("/password-reset",status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(data: ChangePasswordRequest, user: CurrentUser, service: UserService) -> Response:
    await service.reset_password(user=user, password=data.password)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    return response

@router.post("/password-reset-code",status_code=status.HTTP_204_NO_CONTENT)
async def send_password_reset_code(data: ChangePasswordRequest, user: CurrentUser, service: UserService) -> Response:
    await service.reset_password(user=user, password=data.password)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    return response