from datetime import datetime
from typing import ClassVar, Self

from pydantic import ConfigDict, BaseModel

from app.events.routing_keys import RoutingKeys
from app.events.base import Event, UserData, IssueData, ProjectData
from app.infrastructure.db.models import Issue, User
from app.modules.issue.priority import IssuePriority
from app.modules.issue.status import IssueStatus
from app.utils.func_utils import to


class IssueDataDetail(BaseModel):
    title: str
    description: str | None
    
    status: IssueStatus
    priority: IssuePriority
    
    due_date: datetime
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BaseIssueEvent(Event):
    project: ProjectData
    issue: IssueData
    author: UserData
    assignee: UserData | None
    issue_data: IssueDataDetail

    @classmethod
    def from_models(cls, issue: Issue, author: User) -> Self:
        return cls(
            project=to(ProjectData, issue.project),
            issue=to(IssueData, issue),
            author=to(UserData, author),
            assignee=to(UserData, issue.assignee) if issue.assignee else None,
            issue_data=to(IssueDataDetail, issue)
        )
    
    
class IssueCreatedEvent(BaseIssueEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.ISSUE_CREATED


class IssueUpdatedEvent(BaseIssueEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.ISSUE_UPDATED


class IssueDeletedEvent(BaseIssueEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.ISSUE_DELETED


class IssueAssignedEvent(BaseIssueEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.ISSUE_ASSIGNED


class IssueStatusChangedEvent(BaseIssueEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.ISSUE_STATUS_CHANGED


class IssuePriorityChangedEvent(BaseIssueEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.ISSUE_PRIORITY_CHANGED


class IssueDueDateChangedEvent(BaseIssueEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.ISSUE_DUE_DATE_CHANGED

    