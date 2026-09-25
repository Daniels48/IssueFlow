from app.workers.websocket.message import create_message
from app.workers.websocket.project_cache import ProjectCache
from app.workers.websocket.dispatcher import dispatcher
from app.workers.websocket.notification import NotificationService
from app.workers.websocket.schemas import EventEnvelope
from app import events




@dispatcher.register(events.MemberAddedEvent)
async def member_add(event: events.MemberAddedEvent, envelope: EventEnvelope):
    await ProjectCache.add_member(event.project.public_id, event.member.public_id)
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.MemberDeletedEvent)
async def member_remove(event: events.MemberDeletedEvent, envelope: EventEnvelope):
    await ProjectCache.remove_member(event.project.public_id, event.member.public_id)
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id

@dispatcher.register(events.MemberUpdatedEvent)
async def member_change_role(event: events.MemberUpdatedEvent, envelope: EventEnvelope):
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id