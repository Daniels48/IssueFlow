from datetime import datetime
from typing import ClassVar, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events.base import Event, IssueData, ProjectData, UserData
from app.events.routing_keys import RoutingKeys
from app.infrastructure.db.models import Comment, Issue, User
from app.utils.func_utils import to


class CommentData(BaseModel):
    public_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BaseCommentEvent(Event):
    project: ProjectData
    issue: IssueData
    author: UserData
    comment: CommentData

    @classmethod
    def from_models(cls,issue: Issue,author: User,comment: Comment) -> Self:
        return cls(
            project=to(ProjectData, issue.project),
            issue=to(IssueData, issue),
            author=to(UserData, author),
            comment=to(CommentData, comment)
        )


class CommentCreatedEvent(BaseCommentEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.COMMENT_CREATED
    
    
class CommentUpdatedEvent(BaseCommentEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.COMMENT_UPDATED


class CommentDeletedEvent(BaseCommentEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.COMMENT_DELETED