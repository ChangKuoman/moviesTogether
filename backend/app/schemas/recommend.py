from pydantic import BaseModel


class RecommendationOut(BaseModel):
    item_id: int
    title: str
    show_title: str
    type: str
    season_number: int | None
    predicted_rating: float
    confidence: float
    confidence_label: str
    confidence_reason: str
    explanation: str


class ExplanationOut(BaseModel):
    item_id: int
    predicted_rating: float
    confidence: float
    confidence_label: str
    confidence_reason: str
    explanation: str


class FactorItemOut(BaseModel):
    item_id: int
    title: str
    show_title: str
    type: str
    season_number: int | None
    vector: list[float]
    bias: float


class FactorUserOut(BaseModel):
    user_id: int
    name: str
    vector: list[float]
    bias: float


class FactorsOut(BaseModel):
    k: int
    global_mean: float
    items: list[FactorItemOut]
    users: list[FactorUserOut]


class FactorLoadingOut(BaseModel):
    item_id: int
    title: str
    show_title: str
    loading: float


class FactorTopItemsOut(BaseModel):
    factor_index: int
    top: list[FactorLoadingOut]
    bottom: list[FactorLoadingOut]


class MapPointOut(BaseModel):
    item_id: int
    title: str
    show_title: str
    type: str
    season_number: int | None
    x: float
    y: float
    genres: list[str] | None
    poster_url: str | None


class MapUserPointOut(BaseModel):
    user_id: int
    name: str
    x: float
    y: float


class MovieMapOut(BaseModel):
    points: list[MapPointOut]
    user_points: list[MapUserPointOut]
    explained_variance: list[float]
    n_components: int
    warning: str | None


class NeighborOut(BaseModel):
    item_id: int
    title: str
    show_title: str
    similarity: float
