from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str = Field( min_length=1,max_length=5000)

    parent_comment_public_id: UUID | None = None


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1,max_length=5000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID

    content: str

    created_at: datetime
    updated_at: datetime


class CommentTreeResponse(CommentResponse):
    replies: list["CommentTreeResponse"] = []
