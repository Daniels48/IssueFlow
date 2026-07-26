from app.events import CommentCreatedEvent, CommentUpdatedEvent, CommentDeletedEvent
from app.workers.websocket.dispatcher import dispatcher
from app.workers.websocket.notification import NotificationService


@dispatcher.register(CommentCreatedEvent)
async def comment_created(event: CommentCreatedEvent) -> None:
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)

@dispatcher.register(CommentUpdatedEvent)
async def comment_updated(event: CommentUpdatedEvent) -> None:
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)

@dispatcher.register(CommentDeletedEvent)
async def comment_delete(event:CommentDeletedEvent) -> None:
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)