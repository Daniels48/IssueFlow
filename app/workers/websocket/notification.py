from uuid import UUID

from app.workers.websocket.cache.project import ProjectCache
from app.workers.websocket.manager import manager


class NotificationService:

    @classmethod
    async def notify_project(cls, project_public_id, message: dict, exclude: UUID | None = None) -> None:
        members = await ProjectCache.get_members(project_public_id)

        if exclude:
            members.discard(exclude)

        await manager.send_to_users(members, message)

    @classmethod
    async def notify_all(cls, message: dict) -> None:
        await manager.broadcast(message)