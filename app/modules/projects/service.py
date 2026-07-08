from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import User
from app.infrastructure.db.models.model_projects import Project
from app.modules.auth.dependencies import DBSession
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schema import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self,repository: ProjectRepository,db: AsyncSession):
        self.repository = repository
        self.db = db

    async def create(self, data: ProjectCreate, current_user: User) -> Project:
        project = Project(name=data.name, description=data.description, owner_id=current_user.id)
        project = await self.repository.create(db=self.db, project=project)
        await self.db.commit()
        return project

    async def get_all(self, current_user: User) -> list[Project]:
        return await self.repository.get_all_by_owner( db=self.db,owner_id=current_user.id)

    async def get_by_public_id(self, public_id: UUID, current_user: User) -> Project:
        project = await self.repository.get_by_public_id(db=self.db, public_id=public_id)
        if not project:
            raise ValueError("Project not found")

        if project.owner_id != current_user.id:
            raise ValueError("Permission denied")

        return project

    async def update(self, public_id: UUID, data: ProjectUpdate, current_user: User) -> Project:
        project = await self.get_by_public_id(public_id, current_user)

        if data.name is not None:
            project.name = data.name

        if data.description is not None:
            project.description = data.description

        project = await self.repository.update( db=self.db, project=project)
        await self.db.commit()
        return project

    async def delete(self, public_id: UUID, current_user: User) -> None:
        project = await self.get_by_public_id(public_id, current_user)
        await self.repository.delete(db=self.db,project=project)
        await self.db.commit()


async def get_project_service(db: DBSession) -> ProjectService:
    return ProjectService(repository=ProjectRepository(), db=db)


project_service = Annotated[ProjectService, Depends(get_project_service)]