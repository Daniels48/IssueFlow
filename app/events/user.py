from datetime import datetime
from typing import ClassVar, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events.base import Event, UserData
from app.events.routing_keys import RoutingKeys
from app.infrastructure.db.models import Session, User
from app.utils.func_utils import to


class UserDataDetail(BaseModel):
    username: str
    email: str  # email-validator
    is_active: bool
    is_superuser: bool
    email_verified_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    
class SessionDataDetail(BaseModel):
    public_id: UUID
    ip_address: str | None = None
    user_agent: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BaseUserEvent(Event):
    author: UserData
    session_data: SessionDataDetail
    user_detail: UserDataDetail

    @classmethod
    def from_models(cls, author: User, session: Session) -> Self:
        return cls(
            author=to(UserData, author),
            session_data=to(SessionDataDetail, session),
            user_detail=to(UserDataDetail, author),
        )


class UserRegisteredEvent(BaseUserEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_REGISTERED


class UserEmailVerifiedEvent(BaseUserEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_EMAIL_VERIFIED


class UserPasswordChangedEvent(BaseUserEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_PASSWORD_CHANGED


class UserLoggedInEvent(BaseUserEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_LOGGED_IN


class UserLoggedOutEvent(BaseUserEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_LOGGED_OUT


class UserLoggedOutAllEvent(BaseUserEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_LOGGED_OUT_ALL


class UserDeletedEvent(BaseUserEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_DELETED