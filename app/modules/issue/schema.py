from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.comments.schema import CommentTreeResponse
from app.modules.users.schema import UserShortResponse
from app.modules.issue.priority import IssuePriority
from app.modules.issue.status import IssueStatus
from app.modules.issue.transitions import ALLOWED_STATUS_TRANSITIONS_FRONT


class IssueStatusTransitions(BaseModel):
    previous: IssueStatus | None = None
    current: IssueStatus
    next: IssueStatus | None = None

    @classmethod
    def from_status(cls, status: IssueStatus):
        transitions = ALLOWED_STATUS_TRANSITIONS_FRONT.get(status, {})

        return cls.model_validate({**transitions, "current": status})


class IssueCreate(BaseModel):
    title: str
    description: str | None = None

    assignee_id: UUID | None = None
    priority: IssuePriority = IssuePriority.MEDIUM
    due_date: datetime | None = None


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID

    title: str
    description: str | None

    status: IssueStatus
    priority: IssuePriority

    reporter: UserShortResponse
    assignee: UserShortResponse | None

    due_date: datetime | None

    created_at: datetime
    updated_at: datetime


class IssueResponseDetail(IssueResponse):
    model_config = ConfigDict(from_attributes=True)

    comments: list[CommentTreeResponse]
    members: list[UserShortResponse]
    allowed_statuses: IssueStatusTransitions
    priorities: list[IssuePriority]


class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

class IssueUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    title: str | None = None
    description: str | None = None
    updated_at: datetime | None = None


class IssueDueDateUpdate(BaseModel):
    due_date: datetime | None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: datetime | None):
        if value is not None and value < datetime.now(timezone.utc):
            raise ValueError("Due date must be in the future")

        return value

class IssueDueDateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    public_id: UUID
    updated_at: datetime | None

    due_date: datetime | None


class IssueAssigneeUpdate(BaseModel):
    assignee_id: UUID | None = None

class IssueAssigneeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    public_id: UUID
    updated_at: datetime | None

    assignee: UserShortResponse | None = None


class IssuePriorityUpdate(BaseModel):
    priority: IssuePriority

class IssuePriorityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    public_id: UUID
    updated_at: datetime | None

    priority: IssuePriority


class IssueStatusUpdate(BaseModel):
    status: IssueStatus

class IssueStatusBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    public_id: UUID
    updated_at: datetime | None

    status: IssueStatus

class IssueStatusResponse(IssueStatusBaseResponse):
    allowed_statuses: IssueStatusTransitions


class DueDateFilter(str, Enum):
    OVERDUE = "overdue"
    TODAY = "today"
    UPCOMING = "upcoming"

class IssueSort(str, Enum):
    DUE_DATE_ASC = "due_date_asc"
    DUE_DATE_DESC = "due_date_desc"

    PRIORITY_ASC = "priority_asc"
    PRIORITY_DESC = "priority_desc"

    NEWEST = "newest"
    OLDEST = "oldest"

class IssueFilters(BaseModel):
    search: str | None = None
    status: IssueStatus | None = None
    priority: IssuePriority | None = None
    due_date: DueDateFilter | None = None
    sort: IssueSort | None = None