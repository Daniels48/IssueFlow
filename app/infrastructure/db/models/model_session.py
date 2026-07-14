from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import BaseModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.db.models.model_users import User


class Session(BaseModel):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False,index=True)

    refresh_token_hash: Mapped[str] = mapped_column(String(64),unique=True,nullable=False,index=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)

    ip_address: Mapped[str | None] = mapped_column(String(45),nullable=True)

    user_agent: Mapped[str | None] = mapped_column(String(512),nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")