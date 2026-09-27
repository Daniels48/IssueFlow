from uuid import UUID

from app.workers.websocket.project_cache import ProjectCache
from app.workers.websocket.manager import manager


class NotificationService:

    @classmethod
    async def notify_project(cls, project_public_id, message: dict, exclude: UUID | None = None) -> None:
        members = await ProjectCache.get_members(project_public_id)

        if exclude:
            members.discard(exclude)

        await manager.send_to_users(users=members, message=message)

    @classmethod
    async def notify_all(cls, message: dict) -> None:
        await manager.broadcast(message)

    @classmethod
    async def notify_all_except(cls, exclude_id:UUID, message: dict) -> None:
        await manager.broadcast_except(message=message, excluded_user_id=exclude_id)

    @classmethod
    async def notify_user(cls, user_id:UUID, message: dict) -> None:
        await manager.send_to_user(user_public_id=user_id, message=message)

