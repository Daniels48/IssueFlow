from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events import RoutingKeys
from app.events.base import Event_OutBox
from app.events.user import UserEventData
from app.infrastructure.db.models import User, Project


class ProjectEventData(BaseModel):
    public_id: UUID
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectEvent(Event_OutBox):
    aggregate_type: str = "project"

    @classmethod
    def _base_data(cls,project: Project, user: User, occurred_at: datetime) -> dict:
        return {
            "aggregate_id": project.public_id,
            "occurred_at": occurred_at,
            "project": ProjectEventData.model_validate(project),
            "author": UserEventData.model_validate(user),
        }


class ProjectCreatedEvent(ProjectEvent):
    event_type: str = RoutingKeys.PROJECT_CREATED

    @classmethod
    def from_model(cls, project: Project,user: User,occurred_at: datetime) -> Self:
        return cls(**cls._base_data(project=project, user=user, occurred_at=occurred_at))


class ProjectUpdatedEvent(ProjectEvent):
    event_type: str = RoutingKeys.PROJECT_UPDATED

    old_value: ProjectEventData

    @classmethod
    def from_model(cls,old_value: ProjectEventData,project: Project,user: User,occurred_at: datetime) -> Self:
        return cls(
            **cls._base_data(project=project, user=user, occurred_at=occurred_at),
            old_value=old_value,
        )


class ProjectDeletedEvent(ProjectEvent):
    event_type: str = RoutingKeys.PROJECT_DELETED

    @classmethod
    def from_model( cls, project: Project, user: User, occurred_at: datetime) -> Self:
        return cls(**cls._base_data(project=project, user=user, occurred_at=occurred_at))