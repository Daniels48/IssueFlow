from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import BaseModel


if TYPE_CHECKING:
    from app.infrastructure.db.models import Issue, User



class Comment(BaseModel):
    __tablename__ = "comments"

    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    parent_comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )

    content: Mapped[str] = mapped_column(Text,nullable=False)

    replies_count: Mapped[int] = mapped_column(Integer,nullable=False,default=0,server_default="0")

    issue: Mapped["Issue"] = relationship(back_populates="comments",)
    author: Mapped["User"] = relationship(back_populates="comments",)

    parent: Mapped["Comment | None"] = relationship( remote_side="Comment.id",back_populates="children")

    children: Mapped[list["Comment"]] = relationship(back_populates="parent",cascade="all, delete-orphan")

    updated_at: Mapped[datetime] = (
        mapped_column(DateTime(timezone=True),server_default=func.now(), nullable=False)
    )
