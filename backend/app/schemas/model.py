from datetime import datetime

from pydantic import BaseModel


class ModelRunOut(BaseModel):
    id: int
    trained_at: datetime
    k: int
    epochs_run: int
    final_train_rmse: float
    n_ratings_used: int
    lr: float
    reg: float
    global_mean: float

    model_config = {"from_attributes": True}


class ModelStatusOut(BaseModel):
    trained: bool
    stale: bool
    min_ratings_required: int
    current_rating_count: int
    last_run: ModelRunOut | None
