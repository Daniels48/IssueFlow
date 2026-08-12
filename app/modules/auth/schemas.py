from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AccessTokenPayload(BaseModel):
    sub: UUID
    exp: datetime
    iat: datetime
    sid: UUID

class SessionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    updated_at: datetime
    ip_address: str | None
    user_agent: str | None
    is_current: bool = False
