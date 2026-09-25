from app.events import CommentCreatedEvent, CommentDeletedEvent, CommentUpdatedEvent, Event
from app.workers.websocket.dispatcher import dispatcher
from app.workers.websocket.message import create_message
from app.workers.websocket.notification import NotificationService
from app.workers.websocket.schemas import EventEnvelope



@dispatcher.register(CommentCreatedEvent)
async def comment_created(event: CommentCreatedEvent, envelope: EventEnvelope):
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id,result["message"],event.author.public_id)
    event_id = envelope.event_id

@dispatcher.register(CommentUpdatedEvent)
async def comment_updated(event: CommentUpdatedEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id

@dispatcher.register(CommentDeletedEvent)
async def comment_delete(event:CommentDeletedEvent,envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id