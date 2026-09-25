from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class EventEnvelope(BaseModel):
    event_id: UUID
    event_type: str
    aggregate_type: str
    aggregate_id: UUID
    payload: dict
    occurred_at: datetime


class WebSocketEvent(BaseModel):
    event_type: str
    payload: dict[str, Any]
