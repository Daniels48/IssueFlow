from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import TypeAdapter

from app.core.exceptions import AppException, ErrorCode
from app.events.issue import IssueCreatedEvent, IssueUpdateEvent, IssueEventData, IssueDeleteEvent, \
    IssueChangeDueDateEvent, IssueUnAssigneeEvent, IssueChangeAssigneeEvent, IssueChangePriorityEvent, \
    IssueChangeStatusEvent, IssueCloseEvent, IssueReopenEvent
from app.events.outbox import OutboxFactory
from app.infrastructure.db.models import User, Issue, ProjectMember

from app.infrastructure.db.database import DBSession

from app.modules.comments.service import CommentService
from app.modules.issue.priority import IssuePriority
from app.modules.issue import schema as schema

from app.modules.issue.repository import IssueRepository
from app.modules.issue.status import IssueStatus
from app.modules.issue.transitions import ALLOWED_STATUS_TRANSITIONS
from app.modules.project_members.repository import ProjectMemberRepository
from app.modules.projects.repository import ProjectRepository
from app.modules.users.repository import UserRepository
from app.permissions import PermissionContext, Permission, ProjectRBAC
from app.utils.func_utils import to, get_now_dt

ISSUE_LIST_ADAPTER = TypeAdapter(list[schema.IssueResponse])


class IssueService:
    def __init__(self,db: AsyncSession):
        self.rep = IssueRepository()
        self.project_rep = ProjectRepository()
        self.member_rep = ProjectMemberRepository()
        self.user_rep = UserRepository()
        self.db = db

    async def create(self,project_id: UUID, data: schema.IssueCreate, user: User) -> schema.IssueResponse:
        result = await self.project_rep.get_by_public_id_with_current_member(self.db, project_id, user.id)

        if result is None:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found")

        project, current_member = result

        context = PermissionContext(user=user, project=project, member=current_member)
        ProjectRBAC.require(permission=Permission.ISSUE_CREATE, context=context)

        create_data = data.model_dump(exclude_unset=True)

        if not ProjectRBAC.is_admin(context):
            admin_fields = {"assignee_id", "priority", "due_date"}

            if admin_fields & create_data.keys():
                raise AppException(ErrorCode.PERMISSION_DENIED,"You do not have permission to set these fields")

        assignee_id = create_data.pop("assignee_id", None)

        if assignee_id is not None:
            member_assignee = await self.member_rep.get_by_project_and_user_id(self.db, project.id, assignee_id)

            if not member_assignee:
                raise AppException(ErrorCode.USER_IS_NOT_A_PROJECT_MEMBER,"User is not a project member")

            create_data["assignee_id"] = member_assignee.user_id
            create_data["assignee"] = member_assignee.user

        now = get_now_dt()

        issue = Issue(project_id=project.id, reporter_id=user.id, reporter=user, created_at=now, **create_data)

        issue = await self.rep.create(self.db, issue)

        event = IssueCreatedEvent.from_model(issue, user, now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return to(schema.IssueResponse, issue)

    async def get(self, public_id: UUID, user: User) -> schema.IssueResponseDetail | None:
        issue = await self.rep.get_by_public_id_full(self.db, public_id)
        if issue is None:
            raise AppException(ErrorCode.ISSUE_NOT_FOUND, "Issue not found")

        member = await self.member_rep.get_by_project_and_user(self.db, issue.project.id, user.id)

        context = PermissionContext(user=user, project=issue.project, member=member, resource=issue)
        ProjectRBAC.require(permission=Permission.ISSUE_VIEW, context=context)

        return schema.IssueResponseDetail(
            **schema.IssueResponse.model_validate(issue).model_dump(),
            comments=CommentService.build_comment_tree(issue.comments),
            members=[schema.UserShortResponse.model_validate(member.user) for member in issue.project.members],
            priorities=list(IssuePriority),
            allowed_statuses=schema.IssueStatusTransitions.from_status(issue.status)
        )

    async def list(self, project_id: UUID, user: User, filters: schema.IssueFilters) -> list[schema.IssueResponse]:
        project = await self.project_rep.get_by_public_id_no_full(self.db, project_id)

        if not project:
            raise AppException(ErrorCode.PROJECT_NOT_FOUND, "Project not found")

        member = await self.member_rep.get_by_project_and_user(self.db,project.id,user.id)

        context = PermissionContext(user=user, project=project, member=member)
        ProjectRBAC.require(permission=Permission.ISSUE_VIEW, context=context)

        list_issues = await self.rep.get_all_by_project(self.db, project.id, filters)

        return ISSUE_LIST_ADAPTER.validate_python(list_issues)

    async def update(self, public_id: UUID, data: schema.IssueUpdate, user: User) -> schema.IssueUpdateResponse:
        result = await self.rep.get_by_public_id_with_current_member(self.db, public_id, user.id)

        if result is None:
            raise AppException(ErrorCode.ISSUE_NOT_FOUND, "Issue not found")

        issue, member = result

        IssueService.ensure_not_closed(issue)

        context = PermissionContext(user=user, project=issue.project, member=member, resource=issue)
        ProjectRBAC.require(permission=Permission.ISSUE_UPDATE, context=context)

        old_issue = IssueEventData.model_validate(issue)

        changed = False

        if data.description is not None and data.description != issue.description:
            issue.description = data.description
            changed = True

        if data.title is not None and data.title != issue.title:
            issue.title = data.title
            changed = True

        if changed:
            now = get_now_dt()

            issue.updated_at = now

            event = IssueUpdateEvent.from_model(old_issue, issue, user, now)
            self.db.add(OutboxFactory.from_event(event))

            await self.db.commit()

        return to(schema.IssueUpdateResponse, issue)

    async def delete(self,public_id: UUID, user: User) -> None:
        result = await self.rep.get_by_public_id_with_current_member(self.db, public_id, user.id)

        if result is None:
            raise AppException(ErrorCode.ISSUE_NOT_FOUND, "Issue not found")

        issue, member = result

        IssueService.ensure_not_closed(issue)

        context = PermissionContext(user=user, project=issue.project, member=member, resource=issue)
        ProjectRBAC.require(permission=Permission.ISSUE_DELETE, context=context)

        now = get_now_dt()

        issue.updated_at = now
        issue.deleted_at = now

        event = IssueDeleteEvent.from_model(issue, user, now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

    async def update_due_date(self, issue_id: UUID, data: schema.IssueDueDateUpdate, user: User) \
            -> schema.IssueDueDateResponse:
        result = await self.rep.get_by_public_id_with_current_member(self.db, issue_id,user.id)

        if result is None:
            raise AppException(ErrorCode.ISSUE_NOT_FOUND,"Issue not found")

        issue, member = result

        IssueService.ensure_not_closed(issue)

        context = PermissionContext(user=user,project=issue.project,member=member,resource=issue)
        ProjectRBAC.require(permission=Permission.ISSUE_CHANGE_DUE_DATE,context=context)

        if issue.due_date == data.due_date:
            return to(schema.IssueDueDateResponse, issue)

        now = get_now_dt()

        old_value = issue.due_date
        issue.due_date = data.due_date
        issue.updated_at = now

        event = IssueChangeDueDateEvent.from_model(old_value, issue, user, now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return to(schema.IssueDueDateResponse, issue)

    async def update_assignee(self, issue_id: UUID,data: schema.IssueAssigneeUpdate,user: User) \
            -> schema.IssueAssigneeResponse:
        result = await self.rep.get_by_public_id_with_current_member_and_assignee(self.db, issue_id,user.id)

        if result is None:
            raise AppException(ErrorCode.ISSUE_NOT_FOUND,"Issue not found")

        issue, member_current = result

        IssueService.ensure_not_closed(issue)

        context = PermissionContext(user=user, project=issue.project, member=member_current, resource=issue)
        ProjectRBAC.require(permission=Permission.ISSUE_ASSIGNED, context=context)

        now = get_now_dt()

        old_value = issue.assignee

        def set_assignee(assignee_value: ProjectMember | None):
            issue.assignee = assignee_value.user if assignee_value is not None else None
            issue.assignee_id = assignee_value.user_id if assignee_value is not None else None
            issue.updated_at = now

        if data.assignee_id is None:

            if issue.assignee_id is None:
                return to(schema.IssueAssigneeResponse, issue)

            set_assignee(None)

            event = IssueUnAssigneeEvent.from_model(old_value, issue, user, now)

        else:
            member_assignee = await self.member_rep.get_by_project_and_user_id(
                self.db, issue.project_id, data.assignee_id
            )

            if member_assignee is None:
                raise AppException(ErrorCode.USER_IS_NOT_A_PROJECT_MEMBER,"User is not a project member")

            if issue.assignee_id == member_assignee.user_id:
                return to(schema.IssueAssigneeResponse, issue)

            set_assignee(member_assignee)

            event = IssueChangeAssigneeEvent.from_model(old_value, member_assignee.user, issue, user, now)


        self.db.add(OutboxFactory.from_event(event))
        await self.db.commit()

        return to(schema.IssueAssigneeResponse, issue)

    async def update_priority(self,issue_id: UUID,data: schema.IssuePriorityUpdate,user: User) \
            -> schema.IssuePriorityResponse:
        result = await self.rep.get_by_public_id_with_current_member(self.db,issue_id,user.id)

        if result is None:
            raise AppException(ErrorCode.ISSUE_NOT_FOUND,"Issue not found")

        issue, member_current = result

        IssueService.ensure_not_closed(issue)

        context = PermissionContext(user=user,project=issue.project,member=member_current,resource=issue)
        ProjectRBAC.require(permission=Permission.ISSUE_CHANGE_PRIORITY, context=context)

        if issue.priority == data.priority:
            return to(schema.IssuePriorityResponse, issue)

        now = get_now_dt()

        old_value = issue.priority

        issue.priority = data.priority
        issue.updated_at = now

        event = IssueChangePriorityEvent.from_model(old_value, issue, user, now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return to(schema.IssuePriorityResponse, issue)

    async def update_status(self, issue_id: UUID, data: schema.IssueStatusUpdate, user: User) \
            -> schema.IssueStatusResponse:
        result = await self.rep.get_by_public_id_with_current_member(self.db,issue_id,user.id)

        if result is None:
            raise AppException(ErrorCode.ISSUE_NOT_FOUND,"Issue not found")

        issue, member_current = result

        IssueService.ensure_not_closed(issue)

        context = PermissionContext(user=user, project=issue.project, member=member_current,resource=issue)
        ProjectRBAC.require(permission=Permission.ISSUE_CHANGE_STATUS,context=context)

        if issue.status == data.status:
            return self._get_status_response(issue)

        allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(issue.status, set())

        if data.status not in allowed_statuses:
            msg = f"Cannot change status from '{issue.status}' to '{data.status}'"
            raise AppException(ErrorCode.INVALID_STATUS_TRANSITION,msg)

        now = get_now_dt()
        old_value = issue.status

        issue.status = data.status
        issue.updated_at = now

        event = IssueChangeStatusEvent.from_model(old_value, issue, user, now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return self._get_status_response(issue)

    async def close(self, issue_id: UUID, user: User) -> schema.IssueStatusResponse:
        result = await self.rep.get_by_public_id_with_current_member(self.db,issue_id,user.id)

        if result is None:
            raise AppException(ErrorCode.ISSUE_NOT_FOUND,"Issue not found")

        issue, member_current = result

        context = PermissionContext(user=user, project=issue.project, member=member_current, resource=issue)
        ProjectRBAC.require(permission=Permission.ISSUE_CLOSE, context=context)

        if issue.status == IssueStatus.CLOSED:
            raise AppException(ErrorCode.ISSUE_ALREADY_CLOSED,"Issue is already closed")

        now = get_now_dt()

        old_value = issue.status

        issue.status = IssueStatus.CLOSED
        issue.closed_at = now
        issue.closed_by_id = user.id
        issue.updated_at = now

        # await RabbitPublisher.publish(
        #     IssueClosedEvent.from_models(issue, user)
        # )

        event = IssueCloseEvent.from_model(old_value, issue, user, now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return self._get_status_response(issue)

    async def reopen(self,issue_id: UUID,user: User) -> schema.IssueStatusResponse:
        result = await self.rep.get_by_public_id_with_current_member(self.db,issue_id,user.id)

        if result is None:
            raise AppException(ErrorCode.ISSUE_NOT_FOUND,"Issue not found")

        issue, member_current = result

        context = PermissionContext(user=user, project=issue.project,member=member_current,resource=issue)
        ProjectRBAC.require(permission=Permission.ISSUE_REOPEN,context=context)

        if issue.status != IssueStatus.CLOSED:
            raise AppException(ErrorCode.ISSUE_NOT_CLOSED,"Issue is not closed")

        now = get_now_dt()

        issue.status = IssueStatus.OPEN
        issue.closed_at = None
        issue.closed_by_id = None
        issue.updated_at = now

        # await RabbitPublisher.publish(
        #     IssueReopenedEvent.from_models(issue, user)
        # )

        event = IssueReopenEvent.from_model(issue, user, now)
        self.db.add(OutboxFactory.from_event(event))

        await self.db.commit()

        return self._get_status_response(issue)

    @staticmethod
    def _get_status_response(issue: Issue) -> schema.IssueStatusResponse:
        return schema.IssueStatusResponse(
            **schema.IssueStatusBaseResponse.model_validate(issue).model_dump(),
            allowed_statuses=schema.IssueStatusTransitions.from_status(issue.status)
        )

    @staticmethod
    def ensure_not_closed(issue: Issue) -> None:
        if issue.status == IssueStatus.CLOSED:
            raise AppException(ErrorCode.ISSUE_CLOSED,"Issue is closed. Reopen it first.")


async def get_issue_service(db: DBSession) -> IssueService:
    return IssueService(db=db)


issue_service = Annotated[IssueService,Depends(get_issue_service)]


def get_issue_filters(
    search: str | None = Query(default=None, min_length=1),
    status: IssueStatus | None = None,
    priority: IssuePriority | None = None,
    due_date: str | None = None,
    sort: str | None = None,
) -> schema.IssueFilters:
    return schema.IssueFilters(search=search,status=status, priority=priority,due_date=due_date, sort=sort)

issue_filters = Annotated[schema.IssueFilters, Depends(get_issue_filters)]