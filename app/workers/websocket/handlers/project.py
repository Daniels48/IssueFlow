from app.workers.websocket.dispatcher import dispatcher
from app.workers.websocket.message import create_message
from app.workers.websocket.notification import NotificationService
from app import events
from app.workers.websocket.schemas import EventEnvelope



@dispatcher.register(events.ProjectCreatedEvent)
async def create_project(event: events.ProjectCreatedEvent, envelope: EventEnvelope):
    result = create_message(event, envelope)
    await NotificationService.notify_all(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.ProjectDeletedEvent)
async def delete_project(event: events.ProjectDeletedEvent, envelope: EventEnvelope):
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.ProjectUpdatedEvent)
async def updated_project(event: events.ProjectUpdatedEvent, envelope: EventEnvelope):
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id