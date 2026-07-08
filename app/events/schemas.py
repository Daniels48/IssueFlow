from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Event(BaseModel):
    occurred_at: datetime


class IssueCreatedEvent(Event):
    issue_public_id: UUID
    project_public_id: UUID

    reporter_public_id: UUID
    assignee_public_id: UUID | None

    title: str


class IssueAssignedEvent(Event):
    issue_public_id: UUID
    assignee_public_id: UUID


class IssueUpdatedEvent(Event):
    issue_public_id: UUID


class IssueDeletedEvent(Event):
    issue_public_id: UUID


class CommentCreatedEvent(Event):
    comment_public_id: UUID
    issue_public_id: UUID

    author_public_id: UUID

    parent_comment_public_id: UUID | None


class CommentUpdatedEvent(Event):
    comment_public_id: UUID


class CommentDeletedEvent(Event):
    comment_public_id: UUID


class ProjectMemberAddedEvent(Event):
    project_public_id: UUID
    user_public_id: UUID


class ProjectMemberRemovedEvent(Event):
    project_public_id: UUID
    user_public_id: UUID