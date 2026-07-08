from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.project_members.project_role import ProjectRole


class ProjectMemberCreate(BaseModel):
    user_public_id: UUID


class ProjectMemberUpdate(BaseModel):
    role: ProjectRole


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_public_id: UUID
    username: str
    role: ProjectRole