from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db.base import BaseModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.db.models import Issue, ProjectMember, User


class Project(BaseModel):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    issues: Mapped[list["Issue"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    users: Mapped[list["User"]] = relationship(
        secondary="project_members",
        viewonly=True,
    )