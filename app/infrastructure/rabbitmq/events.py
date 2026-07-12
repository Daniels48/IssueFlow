from abc import ABC
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel


class RoutingKeys:
    ISSUE_CREATED = "issue.created"
    ISSUE_ASSIGNED = "issue.assigned"
    ISSUE_UPDATED = "issue.updated"
    ISSUE_DELETED = "issue.deleted"

    COMMENT_CREATED = "comment.created"
    COMMENT_UPDATED = "comment.updated"
    COMMENT_DELETED = "comment.deleted"

    PROJECT_MEMBER_ADDED = "project.member.added"
    PROJECT_MEMBER_REMOVED = "project.member.removed"


class Event(BaseModel, ABC):
    ROUTING_KEY: ClassVar[str]

    occurred_at: datetime


class IssueCreatedEvent(Event):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.ISSUE_CREATED

    issue_public_id: UUID
    project_public_id: UUID

    reporter_public_id: UUID
    assignee_public_id: UUID | None

    title: str


class IssueAssignedEvent(Event):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.ISSUE_ASSIGNED

    issue_public_id: UUID
    assignee_public_id: UUID


# class IssueUpdatedEvent(Event):
#     issue_public_id: UUID
#
#
# class IssueDeletedEvent(Event):
#     issue_public_id: UUID
#
#
# class CommentCreatedEvent(Event):
#     comment_public_id: UUID
#     issue_public_id: UUID
#
#     author_public_id: UUID
#
#     parent_comment_public_id: UUID | None
#
#
# class CommentUpdatedEvent(Event):
#     comment_public_id: UUID
#
#
# class CommentDeletedEvent(Event):
#     comment_public_id: UUID
#
#
# class ProjectMemberAddedEvent(Event):
#     project_public_id: UUID
#     user_public_id: UUID
#
#
# class ProjectMemberRemovedEvent(Event):
#     project_public_id: UUID
#     user_public_id: UUID