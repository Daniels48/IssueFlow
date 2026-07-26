from typing import ClassVar
from uuid import UUID

from app.events.base import Event
from app.events.routing_keys import RoutingKeys


class UserRegisteredEvent(Event):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_REGISTERED

    user_public_id: UUID
    email: str
    username: str


class UserEmailVerifiedEvent(Event):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_EMAIL_VERIFIED

    user_public_id: UUID


class UserPasswordChangedEvent(Event):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_PASSWORD_CHANGED

    user_public_id: UUID


class UserLoggedInEvent(Event):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_LOGGED_IN

    user_public_id: UUID
    session_id: UUID


class UserLoggedOutEvent(Event):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_LOGGED_OUT

    user_public_id: UUID
    session_id: UUID


class UserLoggedOutAllEvent(Event):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_LOGGED_OUT_ALL

    user_public_id: UUID


class UserDeletedEvent(Event):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.USER_DELETED

    user_public_id: UUID