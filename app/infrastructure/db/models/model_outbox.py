from datetime import datetime
from uuid import UUID
from enum import Enum


from sqlalchemy.dialects.postgresql import UUID as PGUUID

from sqlalchemy import String, Integer, DateTime, func, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped
from uuid6 import uuid7

from app.infrastructure.db.base import Base



class OutboxStatus(str, Enum):
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"



class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True),primary_key=True,default=uuid7)

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)

    aggregate_type: Mapped[str] = mapped_column(String(50),nullable=False)

    aggregate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True),nullable=False)

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default=OutboxStatus.PENDING)

    attempts: Mapped[int] = mapped_column(Integer,nullable=False,default=0)

    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,server_default=func.now())

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),nullable=True)

    last_error: Mapped[str | None] = mapped_column(Text,nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index(
            "ix_outbox_pending",
            "status",
            "available_at",
            "created_at",
        ),
    )