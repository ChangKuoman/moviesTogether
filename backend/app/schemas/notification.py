from datetime import datetime

from pydantic import BaseModel

from app.schemas.auth import UserOut


class NotificationOut(BaseModel):
    id: int
    type: str
    actor: UserOut
    created_at: datetime
    read: bool
