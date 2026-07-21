from pydantic import BaseModel


class TmdbStatusOut(BaseModel):
    configured: bool


class TmdbSearchResultOut(BaseModel):
    tmdb_id: int
    title: str
    year: str | None
    poster_url: str | None
    media_type: str


class TmdbSeasonOut(BaseModel):
    season_number: int
    name: str | None
    air_date: str | None
    episode_count: int | None


class ItemFromTmdbCreate(BaseModel):
    tmdb_id: int
    media_type: str  # "movie" | "tv"
    season_number: int | None = None
