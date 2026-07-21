from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.auth import UserOut


class FriendRequestCreate(BaseModel):
    recipient_name: str = Field(min_length=1, max_length=50)


class FriendRequestOut(BaseModel):
    id: int
    requester: UserOut
    recipient: UserOut
    status: str
    created_at: datetime
    responded_at: datetime | None

    model_config = {"from_attributes": True}
