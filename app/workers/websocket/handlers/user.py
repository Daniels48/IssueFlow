from app.events import (
    UserDeletedEvent,
    UserEmailVerifiedEvent,
    UserLoggedInEvent,
    UserLoggedOutAllEvent,
    UserLoggedOutEvent,
    UserPasswordChangedEvent,
    UserRegisteredEvent,
)
from app.workers.websocket.dispatcher import dispatcher
from app.workers.websocket.notification import NotificationService


@dispatcher.register(UserRegisteredEvent)
async def user_register(event: UserRegisteredEvent):
    await NotificationService.notify_all(event.model_dump(mode="json"))


@dispatcher.register(UserEmailVerifiedEvent)
async def user_email_verified(event: UserEmailVerifiedEvent):
    await NotificationService.notify_all(event.model_dump(mode="json"))


@dispatcher.register(UserPasswordChangedEvent)
async def user_password_changed(event: UserPasswordChangedEvent):
    await NotificationService.notify_all(event.model_dump(mode="json"))

@dispatcher.register(UserDeletedEvent)
async def user_deleted(event: UserDeletedEvent):
    await NotificationService.notify_all(event.model_dump(mode="json"))

@dispatcher.register(UserLoggedInEvent)
async def user_logged_in(event: UserLoggedInEvent):
    await NotificationService.notify_all(event.model_dump(mode="json"))

@dispatcher.register(UserLoggedOutEvent)
async def user_logged_out(event: UserLoggedOutEvent):
    await NotificationService.notify_all(event.model_dump(mode="json"))

@dispatcher.register(UserLoggedOutAllEvent)
async def user_logged_all_out(event: UserLoggedOutAllEvent):
    await NotificationService.notify_all(event.model_dump(mode="json"))
