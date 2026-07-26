from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.modules.issue.priority import IssuePriority
from app.modules.issue.schema import IssueResponse
from app.modules.issue.status import IssueStatus
from app.modules.project_members.project_role import ProjectRole


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
    updated_at: datetime

class ProjectListResponse(BaseModel):
    public_id: UUID
    name: str
    description: str | None
    updated_at: datetime
    owner: str

    members_count: int
    issues_count: int
    comments_count: int


class ProjectMemberResponse(BaseModel):
    public_id: UUID
    username: str
    role: ProjectRole


class ProjectDetailResponse(BaseModel):
    public_id: UUID
    name: str
    description: str | None
    owner: str
    created_at: datetime
    updated_at: datetime
    roles: list[str]
    members: list[ProjectMemberResponse]
    issues: list[IssueResponse]
