from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events import RoutingKeys
from app.events.base import Event_OutBox
from app.events.issue_outbox import IssueEventData
from app.events.user_outbox import UserEventData
from app.infrastructure.db.models import User, Comment, Issue, Project


class CommentEventData(BaseModel):
    public_id: UUID
    content: str

    model_config = ConfigDict(from_attributes=True)

class CommentCreatedEvent(Event_OutBox):
    event_type: str = RoutingKeys.COMMENT_CREATED
    aggregate_type: str = "comment"

    comment: CommentEventData
    project: UUID
    issue: IssueEventData
    author: UserEventData


    @classmethod
    def from_model(cls, comment: Comment, user: User, issue: Issue, project: Project, occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=comment.public_id,
            author=UserEventData.model_validate(user),
            occurred_at=occurred_at,
            issue=IssueEventData.model_validate(issue),
            comment=CommentEventData.model_validate(comment),
            project=project,
        )



class CommentUpdatedEvent(Event_OutBox):
    event_type: str = RoutingKeys.COMMENT_UPDATED

    comment: CommentEventData
    issue_id: UUID
    author_id: UUID


    @classmethod
    def from_model(cls, user: User, session_id: UUID, occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=user.public_id,
            user=UserEventData.model_validate(user),
            occurred_at=occurred_at,
            session_id=session_id
        )



class CommentDeletedEvent(Event_OutBoxl):
    event_type: str = RoutingKeys.COMMENT_DELETED

    comment: CommentEventData
    issue_id: UUID
    author_id: UUID


    @classmethod
    def from_model(cls, user: User, session_id: UUID, occurred_at: datetime) -> Self:
        return cls(
            aggregate_id=user.public_id,
            user=UserEventData.model_validate(user),
            occurred_at=occurred_at,
            session_id=session_id
        )
