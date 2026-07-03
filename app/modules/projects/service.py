from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.repository import ProjectRepository


class ProjectService:
    def __init__(self,repository: ProjectRepository,db: AsyncSession):
        self.repository = repository
        self.db = db

    