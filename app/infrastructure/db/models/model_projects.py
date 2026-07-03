from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import BaseModel


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