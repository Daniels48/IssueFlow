from datetime import datetime
from uuid import UUID as PyUUID
from uuid6 import uuid7

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    public_id: Mapped[PyUUID] = (
        mapped_column(PG_UUID(as_uuid=True), unique=True, nullable=False, default=uuid7, index=True)
    )

    created_at: Mapped[datetime] = (
        mapped_column(DateTime(timezone=True),server_default=func.now(), nullable=False)
    )

    updated_at: Mapped[datetime] = (
        mapped_column(DateTime(timezone=True),server_default=func.now(), onupdate=func.now(), nullable=False)
    )

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)