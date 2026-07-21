from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import TypeAdapter

from app.infrastructure.db.models import User, Issue
from app.modules.auth.dependencies import DBSession
from app.modules.comments.service import CommentService
from app.modules.issue.repository import IssueRepository
from app.modules.issue.schema import IssueCreate, IssueUpdate, IssueResponse, IssueResponseDetail, IssueResponseEdit
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.projects.repository import ProjectRepository
from app.modules.users.repository import UserRepository


ISSUE_LIST_ADAPTER = TypeAdapter(list[IssueResponse])


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

    async def create(self,project_id: UUID,data: IssueCreate, user: User) -> IssueResponse:
        project = await self.project_repository.get_by_public_id_no_full(self.db, project_id)

        if not project:
            raise ValueError("Project not found")

        assignee = None

        if data.assignee_public_id:
            assignee = await self.user_repository.get_by_public_id(self.db, data.assignee_public_id)

            if not assignee:
                raise ValueError("User not found")

            member = await self.project_member_repository.get_by_project_and_user(self.db, project.id, assignee.id)

            if not member:
                raise ValueError("User is not a project member")

        issue = Issue(
            project_id=project.id,
            reporter_id=user.id,
            assignee_id=assignee.id if assignee else None,
            title=data.title,
            description=data.description,
            priority=data.priority,
            due_date=data.due_date,
        )

        issue = await self.repository.create(self.db, issue)

        await self.db.commit()

        return IssueResponse.model_validate(issue)

    async def get(self, public_id: UUID) -> IssueResponseDetail | None:
        issue = await self.repository.get_by_public_id_full(self.db, public_id)
        if issue is None:
            return None

        base = IssueResponse.model_validate(issue)
        comments_tree = CommentService.build_comment_tree(issue.comments)

        return IssueResponseDetail(**base.model_dump(), comments=comments_tree)

    async def get_edit(self, public_id: UUID) -> IssueResponseEdit | None:
        issue = await self.repository.get_by_public_id_edit(self.db, public_id)
        if issue is None:
            return None
        return IssueResponseEdit.model_validate(issue)

    async def list(self,project_id: UUID, user: User, query: str | None = None) -> list[IssueResponse]:
        project = await self.project_repository.get_by_public_id_no_full(self.db, project_id)

        if not project:
            raise ValueError("Project not found")

        list_issues = await self.repository.get_all_by_project(self.db, project.id, user.id, query)

        return ISSUE_LIST_ADAPTER.validate_python(list_issues)

    async def update(self,public_id: UUID,data: IssueUpdate) -> IssueResponse:
        issue = await self.repository.get_by_public_id(self.db, public_id)

        if not issue:
            raise ValueError("Issue not found")

        if data.assignee_public_id is not None:
            assignee = await self.user_repository.get_by_public_id(self.db,data.assignee_public_id)

            if not assignee:
                raise ValueError("User not found")

            member = await self.project_member_repository.get_by_project_and_user(self.db, issue.project_id,assignee.id)

            if not member:
                raise ValueError("User is not a project member")

            issue.assignee_id = assignee.id

        update_data = data.model_dump(exclude_unset=True,exclude={"assignee_public_id"})

        for field, value in update_data.items():
            setattr(issue, field, value)

        await self.repository.update(self.db, issue)

        await self.db.commit()

        issue = await self.repository.get_by_public_id_full(self.db, public_id)

        return IssueResponse.model_validate(issue)

    async def delete(self,public_id: UUID) -> None:
        issue = await self.repository.get_by_public_id(self.db, public_id)

        if not issue:
            raise ValueError("Issue not found")

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