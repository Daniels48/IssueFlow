from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3,max_length=50)
    email: EmailStr
    password: str = Field(min_length=8,max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    username: str
    email: EmailStr
    is_active: bool
    email_verified_at: datetime | None
    created_at: datetime