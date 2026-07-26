from datetime import datetime, timezone
from typing import TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

def get_now_dt():
    return datetime.now(timezone.utc)

def to(model: type[T], obj: Any) -> T:
    return model.model_validate(obj)