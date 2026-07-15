from datetime import datetime

from sqlalchemy import Boolean, DateTime, String

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import BaseModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.db.models import Project, Session, Issue, ProjectMember, Comment

class User(BaseModel):
    __tablename__ = "users"


    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # Владелец проектов
    owned_projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
    )

    # Участие в проектах
    project_memberships: Mapped[list["ProjectMember"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Созданные задачи
    reported_issues: Mapped[list["Issue"]] = relationship(
        foreign_keys="Issue.reporter_id",
        back_populates="reporter",
    )

    # Назначенные задачи
    assigned_issues: Mapped[list["Issue"]] = relationship(
        foreign_keys="Issue.assignee_id",
        back_populates="assignee",
    )

    # Комментарии
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )

    # Сессии
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
