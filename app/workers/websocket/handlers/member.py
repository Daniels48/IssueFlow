from app.infrastructure.reddis.project import ProjectCache
from app.workers.websocket.dispatcher import dispatcher
from app.events import ProjectMemberRemovedEvent,ProjectMemberAddedEvent,ProjectMemberRoleChangedEvent
from app.workers.websocket.notification import NotificationService


@dispatcher.register(ProjectMemberAddedEvent)
async def member_add(event: ProjectMemberAddedEvent):
    await ProjectCache.add_member(event.project.public_id, event.member.public_id)
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)


@dispatcher.register(ProjectMemberRemovedEvent)
async def member_remove(event: ProjectMemberRemovedEvent):
    await ProjectCache.remove_member(event.project.public_id, event.member.public_id)
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)
    

@dispatcher.register(ProjectMemberRoleChangedEvent)
async def member_change_role(event: ProjectMemberRoleChangedEvent):
    await NotificationService.notify_project(event.project.public_id, event.model_dump(mode="json"), event.author.public_id)