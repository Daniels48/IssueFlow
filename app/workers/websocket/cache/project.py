from typing import cast
from uuid import UUID

from app.core.config import settings
from app.infrastructure.db.models import Project
from app.workers.websocket.cache.redis import RedisConnection


class ProjectCache:
    PREFIX = f"{settings.redis.prefix}:project"

    @classmethod
    def _key(cls, project_id: UUID) -> str:
        return f"{cls.PREFIX}:{project_id}:members"

    @classmethod
    async def bootstrap(cls,projects: list[Project],) -> None:
        redis = await RedisConnection.get_client()
        pipe = redis.pipeline(transaction=False)
        for project in projects:
            if project.users:
                await pipe.sadd(cls._key(project.public_id),*(str(user.public_id) for user in project.users))

        await pipe.execute()

    @classmethod
    async def get_members(cls,project_id: UUID) -> set[UUID]:
        redis = await RedisConnection.get_client()
        members = cast(set[str], await redis.smembers(cls._key(project_id)))
        return {UUID(member) for member in members}

    @classmethod
    async def add_member(cls,project_id: UUID,user_id: UUID) -> None:
        redis = await RedisConnection.get_client()
        await redis.sadd(cls._key(project_id),str(user_id))

    @classmethod
    async def remove_member(cls,project_id: UUID,user_id: UUID) -> None:
        redis = await RedisConnection.get_client()
        await redis.srem(cls._key(project_id),str(user_id))

    @classmethod
    async def delete_project(cls,project_id: UUID,) -> None:
        redis = await RedisConnection.get_client()
        await redis.delete(cls._key(project_id))