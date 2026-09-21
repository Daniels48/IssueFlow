
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import  select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models import User, ProjectMember, Issue
from app.infrastructure.db.models.model_projects import Project
from app.infrastructure.db.database import DBSession
from app.modules.issue.schema import IssueResponse
from app.modules.project_members.project_role import ProjectRole
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schema import ProjectCreate, ProjectUpdate, ProjectListResponse, ProjectMemberResponse, \
    ProjectDetailResponse, ProjectListBaseResponse
from app.modules.users.schema import UserShortResponse


class ProjectService:
    def __init__(self,repository: ProjectRepository,db: AsyncSession):
        self.repository = repository
        self.db = db

    async def create(self, data: ProjectCreate, current_user: User) -> Project:
        project = Project(name=data.name,description=data.description,owner_id=current_user.id)
        project = await self.repository.create(db=self.db, project=project)
        member = ProjectMember(project_id=project.id,user_id=current_user.id,role=ProjectRole.MEMBER)
        await ProjectMemberRepository.create(db=self.db, member=member)
        await self.db.commit()
        return project


    async def get_all(self, user: User) -> list[ProjectListResponse]:
        rows = await self.repository.get_all_by_user(db=self.db, user_id=user.id, is_admin=user.is_superuser)

        return [
            ProjectListResponse(
                **ProjectListBaseResponse.model_validate(project).model_dump(),
                members_count=members_count,
                issues_count=issues_count,
                comments_count=comments_count,
            )
            for project, members_count, issues_count, comments_count in rows
        ]

    async def get_by_public_id(self, public_id: UUID, current_user: User) -> ProjectDetailResponse:
        project = await self.repository.get_by_public_id(db=self.db, public_id=public_id, user_id=current_user.id)
        if not project:
            raise ValueError("Project not found")

        return ProjectDetailResponse.model_validate(project)


    async def update(self, public_id: UUID, data: ProjectUpdate, current_user: User) -> Project | None:
        project = await self.repository.get_by_public_id_one(self.db, public_id, current_user.id)

        if data.name is not None:
            project.name = data.name

        if data.description is not None:
            project.description = data.description

        project = await self.repository.update(db=self.db, project=project)
        await self.db.commit()
        return project

    async def delete(self, public_id: UUID, current_user: User) -> None:
        project = await self.repository.get_by_public_id_one(self.db, public_id, current_user.id)
        await self.repository.delete(db=self.db,project=project)
        await self.db.commit()


async def get_project_service(db: DBSession) -> ProjectService:
    return ProjectService(repository=ProjectRepository(), db=db)


project_service = Annotated[ProjectService, Depends(get_project_service)]