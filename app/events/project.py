from datetime import datetime
from typing import ClassVar, Self

from pydantic import BaseModel, ConfigDict

from app.events.base import Event, ProjectData, UserData
from app.events.routing_keys import RoutingKeys
from app.infrastructure.db.models import Project, User
from app.utils.func_utils import to


class ProjectDataDetail(BaseModel):
    name: str
    description: str | None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BaseProjectEvent(Event):
    project: ProjectData
    author: UserData
    project_detail: ProjectDataDetail

    @classmethod
    def from_models(cls, project: Project, author: User) -> Self:
        return cls(
            project=to(ProjectData, project),
            author=to(UserData, author),
            project_detail=to(ProjectDataDetail, project)
        )


class ProjectCreatedEvent(BaseProjectEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.PROJECT_CREATED


class ProjectUpdatedEvent(BaseProjectEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.PROJECT_UPDATED


class ProjectDeletedEvent(BaseProjectEvent):
    ROUTING_KEY: ClassVar[str] = RoutingKeys.PROJECT_DELETED