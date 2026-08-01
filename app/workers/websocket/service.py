from app.infrastructure.db.database import AsyncSessionLocal
from app.modules.projects.repository import ProjectRepository
from app.infrastructure.reddis.project import ProjectCache


class CacheBootstrapService:

    @classmethod
    async def bootstrap(cls) -> None:
        async with AsyncSessionLocal() as db:
            projects = await ProjectRepository.get_all_with_users(db)

            await ProjectCache.bootstrap(projects)