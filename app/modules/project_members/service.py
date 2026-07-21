from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import User, ProjectMember
from app.modules.auth.dependencies import DBSession
from app.modules.project_members.project_role import ProjectRole
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.project_members.schema import ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse, \
    ProjectMemberResponse_
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schema import UserShortResponse
from app.modules.users.repository import UserRepository


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

    async def add_member(self, project_id: UUID, data: ProjectMemberCreate, current_user: User) -> ProjectMemberResponse_:
        project = await self.project_repository.get_by_public_id_no_full(self.db, project_id)

        if not project:
            raise ValueError("Project not found")

        if project.owner_id != current_user.id:
            raise ValueError("Permission denied")

        user = await self.user_repository.get_by_public_id(self.db, data.user_public_id)

        if not user:
            raise ValueError("User not found")

        member = await self.repository.user_in_project(self.db, project.id, user.id)

        if member:
            raise ValueError("User already in project")

        member = ProjectMember(project_id=project.id, user_id=user.id, role=ProjectRole.MEMBER)
        member = await self.repository.create(self.db,member)
        await self.db.commit()
        return ProjectMemberResponse_(public_id=user.public_id, username=user.username, role=member.role)


    async def get_members(self, project_id: UUID, current_user: User) -> list[ProjectMemberResponse]:
        project = await self.project_repository.get_by_public_id(self.db, project_id, current_user.id)

        if not project:
            raise ValueError("Project not found")

        if project.owner_id != current_user.id:
            raise ValueError("Permission denied")

        members = await self.repository.get_all_by_project(self.db, project.id)

        return MEMBER_LIST_ADAPTER.validate_python(members)

    async def update_role(self,project_id: UUID, user_id: UUID,data: ProjectMemberUpdate,current_user: User) -> ProjectMemberResponse:
        project = await self.project_repository.get_by_public_id_no_full(self.db, project_id)

        if not project:
            raise ValueError("Project not found")

        if project.owner_id != current_user.id:
            raise ValueError("Permission denied")

        user = await self.user_repository.get_by_public_id(self.db,user_id)

        if not user:
            raise ValueError("User not found")

        member = await self.repository.get_by_project_and_user(self.db,project.id,user.id)

        if not member:
            raise ValueError("Member not found")

        member.role = data.role
        member = await self.repository.update(self.db,member)
        await self.db.commit()
        return ProjectMemberResponse(public_id=user.public_id, username=user.username, role=member.role)

    async def delete_member(self,project_id: UUID,user_id: UUID,current_user: User) -> None:
        project = await self.project_repository.get_by_public_id(self.db, project_id, user_id=current_user.id)

        if not project:
            raise ValueError("Project not found")

        if project.owner_id != current_user.id:
            raise ValueError("Permission denied")

        user = await self.user_repository.get_by_public_id(self.db,user_id)

        if not user:
            raise ValueError("User not found")

        member = await self.repository.get_by_project_and_user(self.db,project.id,user.id)

        if not member:
            raise ValueError("Member not found")

        await self.repository.delete(self.db,member)
        await self.db.commit()

    async def member_in_project(self):
        pass

async def get_member_service(db: DBSession) -> ProjectMemberService:
    return ProjectMemberService(
        repository=ProjectMemberRepository(),
        project_repository=ProjectRepository(),
        user_repository=UserRepository(),
        db=db
    )


MemberService = Annotated[ProjectMemberService,Depends(get_member_service)]