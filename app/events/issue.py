from datetime import datetime
from typing import Self, ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events import RoutingKeys
from app.events.base import Event
from app.events.project import ProjectEventData
from app.events.user import UserEventData
from app.infrastructure.db.models import User, Issue
from app.modules.issue.priority import IssuePriority
from app.modules.issue.status import IssueStatus


class IssueEventData(BaseModel):
    public_id: UUID
    title: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class IssueEvent(Event):
    aggregate_type: ClassVar[str] = "issue"

    issue: IssueEventData
    project: ProjectEventData
    author: UserEventData

    @classmethod
    def _base_data( cls,issue: Issue,user: User,occurred_at: datetime) -> dict:
        return {
            "aggregate_id": issue.public_id,
            "occurred_at": occurred_at,
            "issue": IssueEventData.model_validate(issue),
            "project": ProjectEventData.model_validate(issue.project),
            "author": UserEventData.model_validate(user),
        }

class IssueCreateEventData(BaseModel):
    public_id: UUID
    title: str
    description: str | None = None
    priority: IssuePriority
    assignee: UserEventData | None = None
    due_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class IssueCreatedEvent(IssueEvent):
    event_type: ClassVar[str] = RoutingKeys.ISSUE_CREATED

    issue: IssueCreateEventData
    project: ProjectEventData
    author: UserEventData

    @classmethod
    def from_model(cls, issue: Issue, user: User, occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=issue.public_id,
            occurred_at=occurred_at,
            issue=IssueCreateEventData.model_validate(issue),
            project=ProjectEventData.model_validate(issue.project),
            author=UserEventData.model_validate(user),
        )


class IssueDeleteEvent(IssueEvent):
    event_type: ClassVar[str] = RoutingKeys.ISSUE_DELETED

    @classmethod
    def from_model(cls, issue: Issue, user: User, occurred_at: datetime) -> Self:
        return cls(**cls._base_data(issue, user, occurred_at))


class IssueUpdateEvent(IssueEvent):
    event_type: ClassVar[str] = RoutingKeys.ISSUE_UPDATED

    old_value: IssueEventData

    @classmethod
    def from_model(cls, issue_old: IssueEventData, issue: Issue, user: User, occurred_at: datetime) -> Self:
        return cls(
            **cls._base_data(issue, user, occurred_at),
            old_value=issue_old,
        )


class IssueChangeDueDateEvent(IssueEvent):
    event_type: ClassVar[str] = RoutingKeys.ISSUE_DUE_DATE_CHANGED

    old_value: datetime | None = None
    new_value: datetime | None = None

    @classmethod
    def from_model(cls, old_value: datetime | None, issue: Issue, user: User, occurred_at: datetime) -> Self:
        return cls(
            **cls._base_data(issue, user, occurred_at),
            old_value=old_value,
            new_value=issue.due_date,
        )


class IssueChangeAssigneeEvent(IssueEvent):
    event_type: ClassVar[str] = RoutingKeys.ISSUE_ASSIGNED

    old_value: UserEventData | None = None
    new_value: UserEventData | None = None

    @classmethod
    def from_model(cls, old_value: User | None, new_value: User, issue: Issue, user: User, occurred_at: datetime) -> Self:
        return cls(
            **cls._base_data(issue, user, occurred_at),
            old_value=UserEventData.model_validate(old_value),
            new_value=UserEventData.model_validate(new_value),
        )


class IssueUnAssigneeEvent(IssueEvent):
    event_type: ClassVar[str] = RoutingKeys.ISSUE_UNASSIGNED

    old_value: UserEventData | None = None

    @classmethod
    def from_model(cls, old_value: User, issue: Issue, user: User, occurred_at: datetime) -> Self:
        return cls(
            **cls._base_data(issue, user, occurred_at),
            old_value=UserEventData.model_validate(old_value),
        )


class IssueChangePriorityEvent(IssueEvent):
    event_type: ClassVar[str] = RoutingKeys.ISSUE_PRIORITY_CHANGED

    old_value: IssuePriority
    new_value: IssuePriority

    @classmethod
    def from_model(cls, old_value: IssuePriority, issue: Issue, user: User, occurred_at: datetime) -> Self:
        return cls(
            **cls._base_data(issue, user, occurred_at),
            old_value=old_value,
            new_value=issue.priority
        )


class IssueChangeStatusEvent(IssueEvent):
    event_type: ClassVar[str] = RoutingKeys.ISSUE_STATUS_CHANGED

    old_value: IssueStatus
    new_value: IssueStatus

    @classmethod
    def from_model(cls, old_value: IssueStatus, issue: Issue, user: User, occurred_at: datetime) -> Self:
        return cls(
            **cls._base_data(issue, user, occurred_at),
            old_value=old_value,
            new_value=issue.status
        )


class IssueCloseEvent(IssueEvent):
    event_type: ClassVar[str] = RoutingKeys.ISSUE_CLOSED

    old_value: IssueStatus

    @classmethod
    def from_model(cls, old_value: IssueStatus, issue: Issue, user: User, occurred_at: datetime) -> Self:
        return cls(
            **cls._base_data(issue, user, occurred_at),
            old_value=old_value
        )


class IssueReopenEvent(IssueEvent):
    event_type: ClassVar[str] = RoutingKeys.ISSUE_REOPENED

    @classmethod
    def from_model(cls, issue: Issue, user: User, occurred_at: datetime) -> Self:
        return cls(**cls._base_data(issue, user, occurred_at))