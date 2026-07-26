from app.events import ProjectCreatedEvent, ProjectDeletedEvent, ProjectUpdatedEvent
from app.workers.websocket.dispatcher import dispatcher
from app.workers.websocket.notification import NotificationService


@dispatcher.register(ProjectCreatedEvent)
async def create_project(event: ProjectCreatedEvent):
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)


@dispatcher.register(ProjectDeletedEvent)
async def delete_project(event: ProjectDeletedEvent):
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)


@dispatcher.register(ProjectUpdatedEvent)
async def updated_project(event: ProjectUpdatedEvent):
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)