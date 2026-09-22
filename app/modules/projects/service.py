
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.exceptions import AppException, ErrorCode
from app.events.outbox import OutboxFactory
from app.events.project import ProjectCreatedEvent, ProjectUpdatedEvent, ProjectEventData, ProjectDeletedEvent
from app.infrastructure.db.models import User, ProjectMember, Issue
from app.infrastructure.db.models.model_projects import Project
from app.infrastructure.db.database import DBSession
from app.modules.project_members.project_role import ProjectRole
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schema import ProjectCreate, ProjectUpdate, ProjectListResponse, \
    ProjectDetailResponse, ProjectListBaseResponse, ProjectResponse, ProjectUpdateResponse
from app.permissions import PermissionContext, ProjectRBAC, Permission
from app.utils.func_utils import get_now_dt, to


class ProjectService:
    def __init__(self,repository: ProjectRepository,mem_rep: ProjectMemberRepository, db: AsyncSession):
        self.repository = repository
        self.mem_rep = mem_rep
        self.db = db

    async def create(self, data: ProjectCreate, current_user: User) -> ProjectResponse:
        now = get_now_dt()

        project = Project(name=data.name,description=data.description,owner_id=current_user.id, created_at=now)
        project = await self.repository.create(db=self.db, project=project)

        member = ProjectMember(project_id=project.id,user_id=current_user.id,role=ProjectRole.MEMBER,created_at=now)
        await self.mem_rep.create(db=self.db, member=member)

        event = ProjectCreatedEvent.from_model(project=project, user=current_user, occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return to(ProjectResponse, project)


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

    async def get_one(self, public_id: UUID, user: User) -> ProjectDetailResponse:
        # project = await self.repository.get_by_public_id(db=self.db, public_id=public_id)
        result = await self.repository.get_by_public_id_with_current_member_detail(self.db, public_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found.")

        project, member = result

        context = PermissionContext(user=user, project=project)
        ProjectRBAC.require(permission=Permission.PROJECT_VIEW, context=context)

        return to(ProjectDetailResponse, project)


    async def update(self, public_id: UUID, data: ProjectUpdate, user: User) -> ProjectUpdateResponse:
        result = await self.repository.get_by_public_id_with_current_member(self.db, public_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found.")

        project, member = result

        context = PermissionContext(user=user, project=project, member=member)
        ProjectRBAC.require(permission=Permission.PROJECT_UPDATE, context=context)

        changed = False

        old_value = ProjectEventData.model_validate(project)

        if data.name is not None and data.name != project.name:
            project.name = data.name
            changed = True

        if data.description is not None and data.description != project.description:
            project.description = data.description
            changed = True

        if not changed:
            return to(ProjectUpdateResponse, project)

        now = get_now_dt()

        project.updated_at = now

        event = ProjectUpdatedEvent.from_model(old_value=old_value, project=project, user=user, occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return to(ProjectUpdateResponse, project)

    async def delete(self, public_id: UUID, user: User) -> None:
        result = await self.repository.get_by_public_id_with_current_member(self.db, public_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found.")

        project, member = result

        context = PermissionContext(user=user, project=project, member=member)
        ProjectRBAC.require(permission=Permission.PROJECT_DELETE, context=context)

        now = get_now_dt()
        project.deleted_at = now
        project.updated_at = now

        event = ProjectDeletedEvent.from_model(project=project, user=user, occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()


async def get_project_service(db: DBSession) -> ProjectService:
    return ProjectService(repository=ProjectRepository(), mem_rep=ProjectMemberRepository(), db=db)


project_service = Annotated[ProjectService, Depends(get_project_service)]