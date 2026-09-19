from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.db.models import (
        Comment,
        Issue,
        Project,
        ProjectMember,
        Session,
    )


class User(BaseModel):
    __tablename__ = "users"


    username: Mapped[str] = mapped_column(String(50),unique=True,nullable=False,index=True)

    email: Mapped[str] = mapped_column(String(255),unique=True,nullable=False,index=True)

    password_hash: Mapped[str] = mapped_column(String(255),nullable=False,)

    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),nullable=True,)

    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)

    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),nullable=True)

    owned_projects: Mapped[list["Project"]] = relationship(back_populates="owner")

    project_memberships: Mapped[list["ProjectMember"]] = relationship(back_populates="user",cascade="all, delete-orphan")

    reported_issues: Mapped[list["Issue"]] = relationship(foreign_keys="Issue.reporter_id", back_populates="reporter")

    assigned_issues: Mapped[list["Issue"]] = relationship(foreign_keys="Issue.assignee_id",back_populates="assignee")

    comments: Mapped[list["Comment"]] = relationship(back_populates="author",cascade="all, delete-orphan")

    sessions: Mapped[list["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")