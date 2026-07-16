
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import User, ProjectMember
from app.infrastructure.db.models.model_projects import Project
from app.modules.auth.dependencies import DBSession
from app.modules.project_members.project_role import ProjectRole
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schema import ProjectCreate, ProjectUpdate, ProjectListResponse, ProjectMemberResponse, \
    ProjectDetailResponse, IssueResponse, UserShortResponse


class ProjectService:
    def __init__(self,repository: ProjectRepository,db: AsyncSession):
        self.repository = repository
        self.db = db

    async def create(self, data: ProjectCreate, current_user: User) -> Project:
        project = Project(name=data.name,description=data.description,owner_id=current_user.id)
        project = await self.repository.create(db=self.db, project=project)
        member = ProjectMember(project_id=project.id,user_id=current_user.id,role=ProjectRole.OWNER)
        await ProjectMemberRepository.create(db=self.db, member=member)
        await self.db.commit()
        return project


    async def get_all(self, current_user: User) -> list[ProjectListResponse]:
        rows = await self.repository.get_all_by_user(
            db=self.db,
            user_id=current_user.id,
        )

        return [
            ProjectListResponse(
                public_id=project.public_id,
                name=project.name,
                description=project.description,
                updated_at=project.updated_at,
                owner=project.owner.username,
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

        return ProjectDetailResponse(
            public_id=project.public_id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
            members=[
                ProjectMemberResponse(
                    public_id=member.user.public_id,
                    username=member.user.username,
                    role=member.role,
                )
                for member in project.members
            ],
            issues=[
                IssueResponse(
                    public_id=issue.public_id,
                    name=issue.title,
                    description=issue.description,
                    priority=issue.priority,
                    status=issue.status,
                    reporter=UserShortResponse(public_id=issue.reporter.public_id, username=issue.reporter.username),
                    assignee=UserShortResponse(
                        public_id=issue.assignee.public_id,
                        username=issue.assignee.username
                    ) if issue.assignee else None,
                    due_date=issue.due_date,
                    created_at=issue.created_at,
                    updated_at=issue.updated_at,
                )
                for issue in project.issues
            ],
        )

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