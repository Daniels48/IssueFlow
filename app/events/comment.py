from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events import RoutingKeys
from app.events.base import Event_OutBox
from app.events.issue import IssueEventData
from app.events.project import ProjectEventData
from app.events.user import UserEventData
from app.infrastructure.db.models import User, Comment, Issue


class CommentEventData(BaseModel):
    public_id: UUID
    content: str

    model_config = ConfigDict(from_attributes=True)


class CommentParentData(BaseModel):
    comment: CommentEventData
    author: UserEventData

    model_config = ConfigDict(from_attributes=True)


class CommentCreatedEvent(Event_OutBox):
    event_type: str = RoutingKeys.COMMENT_CREATED
    aggregate_type: str = "comment"

    project: ProjectEventData
    issue: IssueEventData
    author: UserEventData

    comment: CommentEventData
    parent: CommentParentData | None = None

    @classmethod
    def from_model(cls, comment: Comment, user: User, issue: Issue, parent: Comment | None, occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=comment.public_id,
            author=UserEventData.model_validate(user),
            occurred_at=occurred_at,
            issue=IssueEventData.model_validate(issue),
            comment=CommentEventData.model_validate(comment),
            project=ProjectEventData.model_validate(issue.project),
            parent=(
                CommentParentData(
                    comment=CommentEventData.model_validate(parent),
                    author=UserEventData.model_validate(parent.author),
                )
                if parent is not None
                else None
            )
        )


class CommentUpdatedEvent(Event_OutBox):
    event_type: str = RoutingKeys.COMMENT_UPDATED
    aggregate_type: str = "comment"

    comment: CommentEventData
    project: ProjectEventData
    issue: IssueEventData
    author: UserEventData

    old_value: str

    @classmethod
    def from_model(cls, comment: Comment, old_value: str, user: User, occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=comment.public_id,
            author=UserEventData.model_validate(user),
            occurred_at=occurred_at,
            issue=IssueEventData.model_validate(comment.issue),
            comment=CommentEventData.model_validate(comment),
            project=ProjectEventData.model_validate(comment.issue.project),
            old_value=old_value,
        )


class CommentDeletedEvent(Event_OutBox):
    event_type: str = RoutingKeys.COMMENT_DELETED
    aggregate_type: str = "comment"

    comment: CommentEventData
    project: ProjectEventData
    issue: IssueEventData
    author: UserEventData

    @classmethod
    def from_model(cls, comment: Comment, user: User, occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=comment.public_id,
            author=UserEventData.model_validate(user),
            occurred_at=occurred_at,
            issue=IssueEventData.model_validate(comment.issue),
            comment=CommentEventData.model_validate(comment),
            project=ProjectEventData.model_validate(comment.issue.project),
        )
