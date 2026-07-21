from datetime import datetime

from pydantic import BaseModel, Field


class RatingUpsert(BaseModel):
    item_id: int
    rating: int = Field(ge=1, le=5)


class RatingOut(BaseModel):
    id: int
    user_id: int
    item_id: int
    rating: int
    rated_at: datetime
    item_title: str
    item_show_title: str
    item_type: str
    item_season_number: int | None

    model_config = {"from_attributes": True}
