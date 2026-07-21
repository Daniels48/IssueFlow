from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.comments.schema import CommentResponse
from app.modules.issue.priority import IssuePriority
from app.modules.issue.status import IssueStatus
from app.modules.projects.schema import UserShortResponse


class IssueCreate(BaseModel):
    title: str
    description: str | None = None

    assignee_public_id: UUID | None = None

    priority: IssuePriority = IssuePriority.MEDIUM

    due_date: datetime | None = None


class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

    assignee_public_id: UUID | None = None

    status: IssueStatus | None = None
    priority: IssuePriority | None = None

    due_date: datetime | None = None


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID

    title: str
    description: str | None

    status: IssueStatus
    priority: IssuePriority

    due_date: datetime | None

    reporter: UserShortResponse
    assignee: UserShortResponse | None

    created_at: datetime
    updated_at: datetime


class IssueResponseEdit(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID

    title: str
    description: str | None

    status: IssueStatus
    priority: IssuePriority
    statuses: list[IssueStatus]

    due_date: datetime | None

    assignee: UserShortResponse | None

    members: list[UserShortResponse]

    created_at: datetime
    updated_at: datetime


class IssueResponseDetail(IssueResponse):
    comments: list[CommentResponse]
