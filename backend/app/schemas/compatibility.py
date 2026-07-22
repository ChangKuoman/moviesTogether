from pydantic import BaseModel

from app.schemas.auth import UserOut


class AgreementItemOut(BaseModel):
    item_id: int
    title: str
    show_title: str
    user_a_rating: float
    user_b_rating: float
    diff: float


class GenreBreakdownOut(BaseModel):
    genre: str
    user_a_avg: float
    user_b_avg: float


class CompatibilityOut(BaseModel):
    user_a: UserOut
    user_b: UserOut
    score_pct: float
    overlap_count: int
    top_agreements: list[AgreementItemOut]
    top_disagreements: list[AgreementItemOut]
    both_watched: list[AgreementItemOut]
    genre_breakdown: list[GenreBreakdownOut]


class CompatibilityPairOut(BaseModel):
    user_a_id: int
    user_b_id: int
    score_pct: float
    overlap_count: int


class CompatibilityMatrixOut(BaseModel):
    users: list[UserOut]
    pairs: list[CompatibilityPairOut]


class WatchTogetherItemOut(BaseModel):
    item_id: int
    title: str
    show_title: str
    type: str
    season_number: int | None
    predicted_a: float
    predicted_b: float
    watch_together_score: float
    rated_by_a: bool
    rated_by_b: bool
