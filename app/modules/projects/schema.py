from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectResponse(BaseModel):
    public_id: UUID
    name: str
    description: str | None
    created_at: datetime