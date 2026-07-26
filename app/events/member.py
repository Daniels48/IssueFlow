from datetime import datetime
from typing import ClassVar, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events.base import Event, UserData, ProjectData, IssueData
from app.events.routing_keys import RoutingKeys
from app.infrastructure.db.models import Issue, User, ProjectMember, Project
from app.modules.project_members.project_role import ProjectRole
from app.utils.func_utils import to


class MemberData(BaseModel):
    public_id: UUID
    
    username: str
    role: ProjectRole

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_models(cls,user: User,member: ProjectMember) -> Self:
        return cls(
            public_id=user.public_id,
            username=user.username,
            role=member.role,
            created_at=member.created_at,
            updated_at=member.updated_at,
        )


class BaseMemberEvent(Event):
    project: ProjectData
    author: UserData
    member: MemberData

    @classmethod
    def from_models(cls, project: Project, author: User, member: ProjectMember) -> Self:
        return cls(
            project=to(ProjectData, project),
            author=to(UserData, author),
            member=MemberData.from_models(member.user, member),
        )


class ProjectMemberAddedEvent(BaseMemberEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.PROJECT_MEMBER_ADDED


class ProjectMemberRoleChangedEvent(BaseMemberEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.PROJECT_MEMBER_ROLE_CHANGED


class ProjectMemberRemovedEvent(BaseMemberEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.PROJECT_MEMBER_REMOVED
