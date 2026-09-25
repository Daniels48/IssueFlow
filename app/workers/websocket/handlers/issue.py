from app import events
from app.workers.websocket.dispatcher import dispatcher
from app.workers.websocket.message import create_message
from app.workers.websocket.notification import NotificationService
from app.workers.websocket.schemas import EventEnvelope


@dispatcher.register(events.IssueCreatedEvent)
async def issue_created(event: events.IssueCreatedEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.IssueUpdateEvent)
async def issue_updated(event: events.IssueUpdateEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.IssueDeleteEvent)
async def issue_deleted(event: events.IssueDeleteEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.IssueChangeStatusEvent)
async def issue_changed_status(event: events.IssueChangeStatusEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.IssueChangePriorityEvent)
async def issue_changed_priority(event: events.IssueChangePriorityEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.IssueChangeDueDateEvent)
async def issue_changed_due_date(event: events.IssueChangeDueDateEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id

@dispatcher.register(events.IssueChangeAssigneeEvent)
async def issue_assignee(event: events.IssueChangeAssigneeEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.IssueUnAssigneeEvent)
async def issue_un_assignee(event: events.IssueUnAssigneeEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.IssueCloseEvent)
async def issue_close(event: events.IssueCloseEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id


@dispatcher.register(events.IssueReopenEvent)
async def issue_reopen(event: events.IssueReopenEvent, envelope: EventEnvelope) -> None:
    result = create_message(event, envelope)
    await NotificationService.notify_project(event.project.public_id, result["message"], event.author.public_id)
    event_id = envelope.event_id