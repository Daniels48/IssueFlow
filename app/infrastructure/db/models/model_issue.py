from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import BaseModel
from app.modules.issue.priority import IssuePriority
from app.modules.issue.status import IssueStatus


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.db.models.model_projects import Project

class Issue(BaseModel):
    __tablename__ = "issues"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=False)

    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[IssueStatus] = mapped_column(default=IssueStatus.OPEN, nullable=False)

    priority: Mapped[IssuePriority] = mapped_column(default=IssuePriority.MEDIUM, nullable=False)

    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship(
        back_populates="issues",
    )