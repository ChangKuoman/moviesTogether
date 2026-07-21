from pydantic import BaseModel


class HybridItemOut(BaseModel):
    item_id: int
    title: str
    show_title: str
    type: str
    season_number: int | None
    collaborative_score: float
    content_score: float
    hybrid_score: float


class HybridOut(BaseModel):
    w_collab: float
    w_content: float
    items: list[HybridItemOut]
