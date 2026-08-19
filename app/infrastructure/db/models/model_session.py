from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import BaseModel

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

    browser: Mapped[str | None] = mapped_column(String(100),nullable=True)

    browser_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    os: Mapped[str | None] = mapped_column(String(100),nullable=True)

    os_distribution: Mapped[str | None] = mapped_column( String(100),nullable=True)

    device_type: Mapped[str | None] = mapped_column(String(20),nullable=True)

    # Client
    timezone: Mapped[str | None] = mapped_column(String(100), nullable=True)

    language: Mapped[str | None] = mapped_column(String(20),nullable=True)

    screen_width: Mapped[int | None] = mapped_column(nullable=True)

    screen_height: Mapped[int | None] = mapped_column(nullable=True)

    dpr: Mapped[float | None] = mapped_column(nullable=True)

    # Geo
    country: Mapped[str | None] = mapped_column(String(100),nullable=True)

    city: Mapped[str | None] = mapped_column(String(100),nullable=True)

    state: Mapped[str | None] = mapped_column(String(100),nullable=True)

    accuracy: Mapped[float | None] = mapped_column(Float,nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")