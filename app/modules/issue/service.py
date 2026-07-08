from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import User, Issue
from app.modules.auth.dependencies import DBSession
from app.modules.issue.repository import IssueRepository
from app.modules.issue.schema import IssueCreate, IssueUpdate
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.projects.repository import ProjectRepository
from app.modules.users.repository import UserRepository


class IssueService:
    def __init__(
        self,
        repository: IssueRepository,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        user_repository: UserRepository,
        db: AsyncSession,
    ):
        self.repository = repository
        self.project_repository = project_repository
        self.project_member_repository = project_member_repository
        self.user_repository = user_repository
        self.db = db

    async def create(self,project_id: UUID,data: IssueCreate, current_user: User) -> Issue:
        project = await self.project_repository.get_by_public_id(self.db,project_id)

        if not project:
            raise ValueError("Project not found")

        assignee = None

        if data.assignee_public_id:
            assignee = await self.user_repository.get_by_public_id(self.db,data.assignee_public_id)

            if not assignee:
                raise ValueError("User not found")

            member = await self.project_member_repository.get_by_project_and_user(self.db, project.id, assignee.id)

            if not member:
                raise ValueError("User is not a project member")

        issue = Issue(
            project_id=project.id,
            reporter_id=current_user.id,
            assignee_id=assignee.id if assignee else None,
            title=data.title,
            description=data.description,
            priority=data.priority,
            due_date=data.due_date,
        )

        issue = await self.repository.create(self.db, issue)

        await self.db.commit()

        return issue

    async def get_all( self,project_id: UUID) -> list[Issue]:
        project = await self.project_repository.get_by_public_id(self.db,project_id,)

        if not project:
            raise ValueError("Project not found")

        return await self.repository.get_all_by_project(self.db,project.id)

    async def get_by_public_id(self,public_id: UUID,) -> Issue:
        issue = await self.repository.get_by_public_id(self.db,public_id)

        if not issue:
            raise ValueError("Issue not found")

        return issue

    async def update(self,public_id: UUID,data: IssueUpdate) -> Issue:
        issue = await self.get_by_public_id(public_id)

        if data.assignee_public_id is not None:
            assignee = await self.user_repository.get_by_public_id(self.db,data.assignee_public_id)

            if not assignee:
                raise ValueError("User not found")

            member = await self.project_member_repository.get_by_project_and_user(self.db, issue.project_id,assignee.id)

            if not member:
                raise ValueError("User is not a project member")

            issue.assignee_id = assignee.id

        if data.title is not None:
            issue.title = data.title

        if data.description is not None:
            issue.description = data.description

        if data.status is not None:
            issue.status = data.status

        if data.priority is not None:
            issue.priority = data.priority

        if data.due_date is not None:
            issue.due_date = data.due_date

        issue = await self.repository.update( self.db,issue)

        await self.db.commit()

        return issue

    async def delete(self,public_id: UUID) -> None:
        issue = await self.get_by_public_id(public_id)

        await self.repository.delete(self.db, issue)

        await self.db.commit()


async def get_issue_service(db: DBSession) -> IssueService:
    return IssueService(
        repository=IssueRepository(),
        project_repository=ProjectRepository(),
        project_member_repository=ProjectMemberRepository(),
        user_repository=UserRepository(),
        db=db
    )


issue_service = Annotated[IssueService,Depends(get_issue_service)]