from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccessTokenPayload(BaseModel):
    sub: UUID
    exp: datetime
    iat: datetime