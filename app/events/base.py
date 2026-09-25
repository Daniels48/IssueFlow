from abc import ABC
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel



class Event(BaseModel, ABC):
    event_type: ClassVar[str]
    aggregate_type: ClassVar[str]

    aggregate_id: UUID
    occurred_at: datetime