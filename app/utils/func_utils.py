from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Enum
from typing import TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

def get_now_dt():
    return datetime.now(timezone.utc)

def to(model: type[T], obj: Any) -> T:
    return model.model_validate(obj)


def pg_enum(enum_cls: type[PyEnum], name: str) -> Enum:
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda enum: [item.value for item in enum],
    )