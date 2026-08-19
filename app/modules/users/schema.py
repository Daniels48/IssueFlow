from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr



class UserShortResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    username: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    username: str
    email: EmailStr
    is_active: bool
    email_verified_at: datetime | None
    created_at: datetime
    password_changed_at: datetime | None