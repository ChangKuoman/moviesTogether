from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    type: str = Field(pattern="^(movie|season)$")
    season_number: int | None = Field(default=None, ge=1)
    year: int | None = Field(default=None, ge=1870, le=2100)

    @field_validator("season_number")
    @classmethod
    def season_number_required_for_seasons(cls, v, info):
        if info.data.get("type") == "season" and v is None:
            raise ValueError("season_number is required for type=season")
        if info.data.get("type") == "movie" and v is not None:
            raise ValueError("season_number must be omitted for type=movie")
        return v


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    year: int | None = Field(default=None, ge=1870, le=2100)
    genres: list[str] | None = None
    overview: str | None = None
    director: str | None = None
    runtime: int | None = None


class ItemOut(BaseModel):
    id: int
    title: str
    type: str
    season_number: int | None
    show_title: str
    year: int | None
    tmdb_id: int | None
    genres: list[str] | None
    overview: str | None
    poster_url: str | None
    director: str | None
    cast: list[str] | None
    runtime: int | None
    source: str
    created_at: datetime
    added_at: datetime | None  # when the current user added it to their library

    model_config = {"from_attributes": True}


class ShowGroupOut(BaseModel):
    show_title: str
    items: list[ItemOut]
