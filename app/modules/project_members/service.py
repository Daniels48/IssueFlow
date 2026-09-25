from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.events import MemberAddedEvent, MemberUpdatedEvent, MemberDeletedEvent, OutboxFactory
from app.infrastructure.db.models import User, ProjectMember
from app.infrastructure.db.database import DBSession
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.project_members.schema import ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse
from app.modules.projects.repository import ProjectRepository
from app.modules.users.repository import UserRepository
from app.permissions import PermissionContext, Permission, ProjectRBAC
from app.utils.func_utils import to, get_now_dt

MEMBER_LIST_ADAPTER = TypeAdapter(list[ProjectMemberResponse])


class ProjectMemberService:
    def __init__(self,db: AsyncSession):
        self.repository = ProjectMemberRepository()
        self.project_repository = ProjectRepository()
        self.user_repository = UserRepository()
        self.db = db

    async def add_member(self, project_id: UUID, data: ProjectMemberCreate, user: User) -> ProjectMemberResponse:
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

        now = get_now_dt()

        member = ProjectMember(project_id=project.id, project=project, user_id=added_user.id, user=added_user, created_at=now)
        member = await self.repository.create(self.db,member)

        event = MemberAddedEvent.from_model(member=member, user=user, occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return to(ProjectMemberResponse, member)

    async def get_members(self, project_id: UUID, user: User) -> list[ProjectMemberResponse]:
        result = await self.project_repository.get_by_public_id_with_current_member(self.db, project_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found")

        project, member_current = result

        context = PermissionContext(user=user, project=project, member=member_current)
        ProjectRBAC.require(permission=Permission.MEMBER_VIEW, context=context)

        members = await self.repository.get_all_by_project(self.db, project.id)

        return MEMBER_LIST_ADAPTER.validate_python(members)

    async def update_role(self,project_id: UUID, user_id: UUID,data: ProjectMemberUpdate,user: User) -> ProjectMemberResponse:
        result = await self.project_repository.get_by_public_id_with_current_member(self.db, project_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found")

        project, member_current = result

        context = PermissionContext(user=user, project=project, member=member_current)
        ProjectRBAC.require(permission=Permission.MEMBER_ROLE_UPDATE, context=context)

        member = await self.repository.get_by_project_and_user_id(self.db, project.id, user_id)

        if not member:
            raise AppException(ErrorCode.USER_IS_NOT_A_PROJECT_MEMBER, "Member not found")

        if member.role == data.role:
            return to(ProjectMemberResponse, member)

        now = get_now_dt()

        old_value = member.role
        member.role = data.role
        member.project = project
        member.updated_at = now

        event = MemberUpdatedEvent.from_model(old_value=old_value, member=member, user=user, occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return to(ProjectMemberResponse, member)

    async def delete_member(self,project_id: UUID,user_id: UUID,user: User) -> None:
        result = await self.project_repository.get_by_public_id_with_current_member(self.db, project_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found")

        project, member_current = result

        context = PermissionContext(user=user, project=project, member=member_current)
        ProjectRBAC.require(permission=Permission.MEMBER_REMOVE, context=context)

        member = await self.repository.get_by_project_and_user_id(self.db, project.id, user_id)

        if not member:
            raise AppException(ErrorCode.USER_IS_NOT_A_PROJECT_MEMBER, "Member not found")

        now = get_now_dt()
        member.project = project

        event = MemberDeletedEvent.from_model(member=member, user=user, occurred_at=now)
        self.db.add(OutboxFactory.from_event(event))

        await self.repository.delete(self.db, member)

        await self.db.commit()


async def get_member_service(db: DBSession) -> ProjectMemberService:
    return ProjectMemberService(db=db)

MemberService = Annotated[ProjectMemberService,Depends(get_member_service)]