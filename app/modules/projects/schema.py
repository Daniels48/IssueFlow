from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, AliasPath, computed_field

from app.modules.issue.priority import IssuePriority
from app.modules.issue.schema import IssueResponse
from app.modules.issue.status import IssueStatus
from app.modules.project_members.project_role import ProjectRole
from app.modules.users.schema import UserShortResponse


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

class ProjectListBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    name: str
    description: str | None
    updated_at: datetime
    owner: UserShortResponse




class ProjectListResponse(ProjectListBaseResponse):
    model_config = ConfigDict(from_attributes=True)

    members_count: int
    issues_count: int
    comments_count: int


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    public_id: UUID = Field(validation_alias=AliasPath("user", "public_id"))
    username: str = Field(validation_alias=AliasPath("user", "username"))
    role: ProjectRole


class ProjectDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    name: str
    description: str | None
    owner: UserShortResponse
    created_at: datetime
    updated_at: datetime
    members: list[ProjectMemberResponse]
    issues: list[IssueResponse]

    @computed_field
    @property
    def roles(self) -> list[ProjectRole]:
        return list(ProjectRole)

