from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
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

    issue: Mapped[list["Issue"]] = relationship(
        back_populates="comments",
    )
    author: Mapped[list["User"]] = relationship(
        back_populates="comments",
    )
