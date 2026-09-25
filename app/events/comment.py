from datetime import datetime
from typing import Self, ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events import RoutingKeys
from app.events.base import Event
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


class CommentEvent(Event):
    aggregate_type: ClassVar[str] = "comment"

    issue: IssueEventData
    project: ProjectEventData
    author: UserEventData
    comment: CommentEventData

    @classmethod
    def _base_data(cls, comment: Comment,user: User,occurred_at: datetime) -> dict:
        return {
            "aggregate_id": comment.public_id,
            "occurred_at": occurred_at,
            "issue": IssueEventData.model_validate(comment.issue),
            "project": ProjectEventData.model_validate(comment.issue.project),
            "author": UserEventData.model_validate(user),
            "comment": CommentEventData.model_validate(comment),
        }

class CommentCreatedEvent(Event):
    event_type: ClassVar[str] = RoutingKeys.COMMENT_CREATED
    aggregate_type: ClassVar[str] = "comment"

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


class CommentUpdatedEvent(CommentEvent):
    event_type: ClassVar[str] = RoutingKeys.COMMENT_UPDATED

    old_value: str

    @classmethod
    def from_model(cls,comment: Comment,old_value: str, user: User,occurred_at: datetime) -> Self:
        return cls(**cls._base_data(comment, user, occurred_at),old_value=old_value)


class CommentDeletedEvent(CommentEvent):
    event_type: ClassVar[str] = RoutingKeys.COMMENT_DELETED

    @classmethod
    def from_model(cls,comment: Comment,user: User,occurred_at: datetime) -> Self:
        return cls(**cls._base_data(comment, user, occurred_at))