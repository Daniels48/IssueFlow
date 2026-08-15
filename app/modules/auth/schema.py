from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserCreate(BaseModel):
    username: str = Field(min_length=3,max_length=50)
    email: EmailStr
    password: str = Field(min_length=8,max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class AccessTokenPayload(BaseModel):
    sub: UUID
    exp: datetime
    iat: datetime
    sid: UUID

class SessionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    updated_at: datetime
    ip_address: str | None
    user_agent: str | None
    is_current: bool = False


class ChangePasswordRequest(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)
    old_password: str = Field(min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

class ChangeEmailRequest(BaseModel):
    email: EmailStr


class PasswordForgotRequest(BaseModel):
    email: EmailStr

class PasswordResetVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    email: EmailStr

class ResetPasswordVerifyResponse(BaseModel):
    reset_token: str







