from abc import ABC
from datetime import UTC, datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, Field, computed_field




class Event(BaseModel, ABC):
    ROUTING_KEY: ClassVar[str]

    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @computed_field
    @property
    def type(self) -> str:
        return self.ROUTING_KEY




class Event_OutBox(BaseModel, ABC):
    event_type: str
    aggregate_type: str
    aggregate_id: UUID
    occurred_at: datetime