from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events.base import Event_OutBox
from app.events.routing_keys import RoutingKeys
from app.infrastructure.db.models import User


class UserEventData(BaseModel):
    public_id: UUID
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserRegisteredEvent(Event_OutBox):
    event_type: str = RoutingKeys.USER_REGISTERED
    aggregate_type: str = "user"

    user: UserEventData
    session_id: UUID

    @classmethod
    def from_model(cls, user: User, session_id: UUID, occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=user.public_id,
            user=UserEventData.model_validate(user),
            occurred_at=occurred_at,
            session_id=session_id
        )


class UserEmailChangedEvent(Event_OutBox):
    event_type: str = RoutingKeys.USER_EMAIL_CHANGED
    aggregate_type: str = "user"

    user: UserEventData
    old_email: str
    new_email: str

    @classmethod
    def from_model(cls,user: User,old_email: str, new_email: str,occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=user.public_id,
            occurred_at=occurred_at,
            user=UserEventData.model_validate(user),
            old_email=old_email,
            new_email=new_email,
        )


class UserEmailVerifyEvent(Event_OutBox):
    event_type: str = RoutingKeys.USER_EMAIL_VERIFIED
    aggregate_type: str = "user"

    user: UserEventData

    @classmethod
    def from_model(cls,user: User, occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=user.public_id,
            occurred_at=occurred_at,
            user=UserEventData.model_validate(user),
        )


class UserPasswordChangedEvent(Event_OutBox):
    event_type: str = RoutingKeys.USER_PASSWORD_CHANGED
    aggregate_type: str = "user"

    user: UserEventData
    session_ids: list[UUID]

    @classmethod
    def from_model(cls,user: User,session_ids: list[UUID], occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=user.public_id,
            occurred_at=occurred_at,
            user=UserEventData.model_validate(user),
            session_ids=session_ids,
        )


class UserLoggedInEvent(Event_OutBox):
    event_type: str = RoutingKeys.USER_LOGGED_IN
    aggregate_type: str = "user"

    user: UserEventData
    session_id: UUID

    @classmethod
    def from_model(cls, user: User, session_id: UUID, occurred_at: datetime) -> "UserLoggedInEvent":
        return cls(
            aggregate_id=user.public_id,
            occurred_at=occurred_at,
            user=UserEventData.model_validate(user),
            session_id=session_id,
        )


class UserLoggedOutEvent(Event_OutBox):
    event_type: str = RoutingKeys.USER_LOGGED_OUT
    aggregate_type: str = "user"

    user: UserEventData
    session_id: UUID

    @classmethod
    def from_model(cls,user: User,session_id: UUID,occurred_at: datetime) -> "UserLoggedOutEvent":
        return cls(
            aggregate_id=user.public_id,
            occurred_at=occurred_at,
            user=UserEventData.model_validate(user),
            session_id=session_id,
        )


class UserLoggedOutAllEvent(Event_OutBox):
    event_type: str = RoutingKeys.USER_LOGGED_OUT_ALL
    aggregate_type: str = "user"

    user: UserEventData
    session_ids: list[UUID]

    @classmethod
    def from_model(cls,user: User, session_ids: list[UUID], occurred_at: datetime) -> "UserLoggedOutAllEvent":
        return cls(
            aggregate_id=user.public_id,
            occurred_at=occurred_at,
            user=UserEventData.model_validate(user),
            session_ids=session_ids,
        )


class UserEmailVerificationRequestedEvent(Event_OutBox):
    event_type: str = RoutingKeys.USER_EMAIL_VERIFICATION_REQUESTED
    aggregate_type: str = "user"

    user: UserEventData

    @classmethod
    def from_model(cls, user: User,occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=user.public_id,
            occurred_at=occurred_at,
            user=UserEventData.model_validate(user),
        )


class UserPasswordResetRequestedEvent(Event_OutBox):
    event_type: str = RoutingKeys.USER_PASSWORD_RESET_REQUESTED
    aggregate_type: str = "user"

    user: UserEventData

    @classmethod
    def from_model(cls,user: User,occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=user.public_id,
            occurred_at=occurred_at,
            user=UserEventData.model_validate(user),
        )


class UserDeletedEvent(Event_OutBox):
    event_type: str = RoutingKeys.USER_DELETED
    aggregate_type: str = "user"

    user: UserEventData

    @classmethod
    def from_model(cls,user: User,occurred_at: datetime) -> "UserDeletedEvent":
        return cls(
            aggregate_id=user.public_id,
            occurred_at=occurred_at,
            user=UserEventData.model_validate(user),
        )