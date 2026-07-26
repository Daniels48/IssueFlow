from app.events import (
    UserRegisteredEvent, UserEmailVerifiedEvent, UserPasswordChangedEvent, UserDeletedEvent,
    UserLoggedInEvent, UserLoggedOutEvent, UserLoggedOutAllEvent
)
from app.workers.websocket.dispatcher import dispatcher
from app.workers.websocket.notification import NotificationService


@dispatcher.register(UserRegisteredEvent)
async def user_register(event: UserRegisteredEvent):
    pass
    # await NotificationService.notify_project(
    #     event.project.public_id, event.model_dump(mode="json"), event.author.public_id
    # )


@dispatcher.register(UserEmailVerifiedEvent)
async def user_email_verified(event: UserEmailVerifiedEvent):
    pass
    # await NotificationService.notify_project(
    #     event.project.public_id, event.model_dump(mode="json"), event.author.public_id
    # )


@dispatcher.register(UserPasswordChangedEvent)
async def user_password_changed(event: UserPasswordChangedEvent):
    pass
    # await NotificationService.notify_project(
    #     event.project.public_id, event.model_dump(mode="json"), event.author.public_id
    # )

@dispatcher.register(UserDeletedEvent)
async def user_deleted(event: UserDeletedEvent):
    pass
    # await NotificationService.notify_project(
    #     event.project.public_id, event.model_dump(mode="json"), event.author.public_id
    # )

@dispatcher.register(UserLoggedInEvent)
async def user_logged_in(event: UserLoggedInEvent):
    pass
    # await NotificationService.notify_project(
    #     event.project.public_id, event.model_dump(mode="json"), event.author.public_id
    # )

@dispatcher.register(UserLoggedOutEvent)
async def user_logged_out(event: UserLoggedOutEvent):
    pass
    # await NotificationService.notify_project(
    #     event.project.public_id, event.model_dump(mode="json"), event.author.public_id
    # )

@dispatcher.register(UserLoggedOutAllEvent)
async def user_logged_all_out(event: UserLoggedOutAllEvent):
    pass
    # await NotificationService.notify_project(
    #     event.project.public_id, event.model_dump(mode="json"), event.author.public_id
    # )
