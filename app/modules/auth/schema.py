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
    browser: str | None
    browser_version: str | None
    os: str | None
    device_type: str | None
    timezone: str | None
    language: str | None
    screen_width: int | None
    screen_height: int | None
    dpr: float | None
    country: str | None
    city: str | None
    state: str | None
    accuracy: float | None


class ChangePasswordRequest(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)
    old_password: str = Field(min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class ChangeEmailRequest(BaseModel):
    email: EmailStr


class PasswordForgotRequest(BaseModel):
    email: EmailStr


class PasswordForgotVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    email: EmailStr


class PasswordForgotVerifyResponse(BaseModel):
    reset_token: str


class PasswordForgotResetRequest(BaseModel):
    reset_token: str
    new_password: str