from abc import ABC
from datetime import UTC, datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, Field, computed_field, ConfigDict


class UserData(BaseModel):
    public_id: UUID
    username: str

    model_config = ConfigDict(from_attributes=True)
    
class IssueData(BaseModel):
    public_id: UUID
    title: str
    
    model_config = ConfigDict(from_attributes=True)
    
class ProjectData(BaseModel):
    public_id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)
    
class Event(BaseModel, ABC):
    ROUTING_KEY: ClassVar[str]

    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @computed_field
    @property
    def type(self) -> str:
        return self.ROUTING_KEY