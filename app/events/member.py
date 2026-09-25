from datetime import datetime
from typing import Self, ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events import RoutingKeys
from app.events.base import Event
from app.events.issue import IssueEventData
from app.events.project import ProjectEventData
from app.events.user import UserEventData
from app.infrastructure.db.models import ProjectMember, User
from app.modules.project_members.project_role import ProjectRole


class MemberEventData(BaseModel):
    public_id: UUID
    role: ProjectRole

    model_config = ConfigDict(from_attributes=True)


class MemberEvent(Event):
    aggregate_type: ClassVar[str] = "member"

    project: ProjectEventData
    author: UserEventData
    user: UserEventData

    member: MemberEventData


    @classmethod
    def _base_data( cls, member: ProjectMember, author: User, occurred_at: datetime) -> dict:
        return {
            "aggregate_id": member.user.public_id,
            "occurred_at": occurred_at,
            "member": MemberEventData.model_validate(member),
            "user": UserEventData.model_validate(member.user),
            "project": ProjectEventData.model_validate(member.project),
            "author": UserEventData.model_validate(author),
        }


class MemberAddedEvent(MemberEvent):
    event_type: ClassVar[str] = RoutingKeys.PROJECT_MEMBER_ADDED

    @classmethod
    def from_model(cls,member: ProjectMember,user: User, occurred_at: datetime) -> Self:
        return cls(**cls._base_data(member=member, author=user, occurred_at=occurred_at))


class MemberUpdatedEvent(MemberEvent):
    event_type: ClassVar[str] = RoutingKeys.PROJECT_MEMBER_ROLE_CHANGED

    old_value: ProjectRole

    @classmethod
    def from_model(cls,old_value: ProjectRole ,member: ProjectMember,user: User, occurred_at: datetime) -> Self:
        return cls(**cls._base_data(member=member, author=user, occurred_at=occurred_at),old_value=old_value)


class MemberDeletedEvent(MemberEvent):
    event_type: ClassVar[str] = RoutingKeys.PROJECT_MEMBER_REMOVED

    @classmethod
    def from_model(cls,member: ProjectMember,user: User,occurred_at: datetime) -> Self:
        return cls(**cls._base_data(member=member, author=user, occurred_at=occurred_at))