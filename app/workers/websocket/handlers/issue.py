from app.events import IssueCreatedEvent, IssueUpdatedEvent, IssueDeletedEvent
from app.workers.websocket.dispatcher import dispatcher
from app.workers.websocket.notification import NotificationService


@dispatcher.register(IssueCreatedEvent)
async def issue_created(event: IssueCreatedEvent) -> None:
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)


@dispatcher.register(IssueUpdatedEvent)
async def issue_updated(event: IssueUpdatedEvent) -> None:
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)


@dispatcher.register(IssueDeletedEvent)
async def issue_deleted(event: IssueDeletedEvent) -> None:
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)