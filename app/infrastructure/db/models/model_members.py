from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import BaseModel
from app.modules.project_members.project_role import ProjectRole


class ProjectMember(BaseModel):
    __tablename__ = "project_members"

    __table_args__ = (
        UniqueConstraint( "project_id","user_id",name="uq_project_member"),
    )

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"),nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)

    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole, name="project_role"), nullable=False, default=ProjectRole.MEMBER
    )