from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.events import ProjectMemberAddedEvent, ProjectMemberRoleChangedEvent, ProjectMemberRemovedEvent
from app.infrastructure.db.models import User, ProjectMember
from app.infrastructure.rabbitmq import RabbitPublisher
from app.modules.auth.dependencies import DBSession
from app.modules.project_members.project_role import ProjectRole
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.project_members.schema import ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse, \
    ProjectMemberResponse_
from app.modules.projects.repository import ProjectRepository
from app.modules.users.repository import UserRepository
from app.permissions import PermissionContext, Permission, ProjectRBAC


MEMBER_LIST_ADAPTER = TypeAdapter(list[ProjectMemberResponse])


class ProjectMemberService:
    def __init__(
        self,
        repository: ProjectMemberRepository,
        project_repository: ProjectRepository,
        user_repository: UserRepository,
        db: AsyncSession,
    ):
        self.repository = repository
        self.project_repository = project_repository
        self.user_repository = user_repository
        self.db = db

    async def add_member(self, project_id: UUID, data: ProjectMemberCreate, user: User) -> ProjectMemberResponse_:
        result = await self.project_repository.get_by_public_id_with_current_member(self.db, project_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND,"Project not found")

        project, member_current = result

        context = PermissionContext(user=user, project=project, member=member_current)
        ProjectRBAC.require(permission=Permission.MEMBER_ADD, context=context)

        added_user = await self.user_repository.get_by_public_id(self.db, data.user_public_id)

        if not added_user:
            raise AppException(ErrorCode.USER_NOT_FOUND, "User not found")

        user_in_project = await self.repository.user_in_project(self.db, project.id, added_user.id)

        if user_in_project:
            raise AppException(ErrorCode.MEMBER_ALREADY_IN_PROJECT, "Member already in project")

        member = ProjectMember(project_id=project.id, user_id=added_user.id, role=ProjectRole.MEMBER)
        member = await self.repository.create(self.db,member)
        await self.db.commit()

        await RabbitPublisher.publish(ProjectMemberAddedEvent.from_models(project, user, member))
        
        return ProjectMemberResponse_(public_id=added_user.public_id, username=added_user.username, role=member.role)


    async def get_members(self, project_id: UUID, user: User) -> list[ProjectMemberResponse]:
        result = await self.project_repository.get_by_public_id_with_current_member(self.db, project_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found")

        project, member_current = result

        context = PermissionContext(user=user, project=project, member=member_current)
        ProjectRBAC.require(permission=Permission.MEMBER_VIEW, context=context)

        members = await self.repository.get_all_by_project(self.db, project.id)

        return MEMBER_LIST_ADAPTER.validate_python(members)

    async def update_role(self,project_id: UUID, user_id: UUID,data: ProjectMemberUpdate,user: User) -> ProjectMemberResponse_:
        result = await self.project_repository.get_by_public_id_with_current_member(self.db, project_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found")

        project, member_current = result

        context = PermissionContext(user=user, project=project, member=member_current)
        ProjectRBAC.require(permission=Permission.MEMBER_ROLE_UPDATE, context=context)

        member = await self.repository.get_by_project_and_user_public_id(self.db, project.id, user_id)

        if not member:
            raise AppException(ErrorCode.USER_IS_NOT_A_PROJECT_MEMBER, "Member not found")

        member.role = data.role
        member = await self.repository.update(self.db,member)
        await self.db.commit()

        await RabbitPublisher.publish(
            ProjectMemberRoleChangedEvent.from_models(project, user, member)
        )
        
        return ProjectMemberResponse_(public_id=member.user.public_id, username=member.user.username, role=member.role)

    async def delete_member(self,project_id: UUID,user_id: UUID,user: User) -> None:
        result = await self.project_repository.get_by_public_id_with_current_member(self.db, project_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found")

        project, member_current = result

        context = PermissionContext(user=user, project=project, member=member_current)
        ProjectRBAC.require(permission=Permission.MEMBER_REMOVE, context=context)

        member = await ProjectMemberRepository.get_by_project_and_user_public_id(self.db, project.id, user_id)

        if not member:
            raise AppException(ErrorCode.USER_IS_NOT_A_PROJECT_MEMBER, "Member not found")

        await self.repository.delete(self.db,member)
        await self.db.commit()

        await RabbitPublisher.publish(ProjectMemberRemovedEvent.from_models(project, user, member))


async def get_member_service(db: DBSession) -> ProjectMemberService:
    return ProjectMemberService(
        repository=ProjectMemberRepository(),
        project_repository=ProjectRepository(),
        user_repository=UserRepository(),
        db=db
    )


MemberService = Annotated[ProjectMemberService,Depends(get_member_service)]