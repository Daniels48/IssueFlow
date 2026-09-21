from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.events import RoutingKeys
from app.events.base import Event_OutBox
from app.events.user import UserEventData
from app.infrastructure.db.models import User, Comment


class ProjectEventData(BaseModel):
    public_id: UUID
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)