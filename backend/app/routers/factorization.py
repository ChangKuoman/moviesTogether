from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.constants import MIN_RATINGS_FOR_TRAIN
from app.database import get_db
from app.deps import get_current_user
from app.models.item import Item
from app.models.rating import Rating
from app.models.user import User
from app.schemas.model import ModelRunOut, ModelStatusOut
from app.schemas.recommend import (
    FactorItemOut,
    FactorLoadingOut,
    FactorsOut,
    FactorTopItemsOut,
    FactorUserOut,
)
from app.services import model_service

router = APIRouter(prefix="/api/model", tags=["model"])


def _factors_or_422(db: Session) -> dict:
    factors = model_service.load_latest_factors(db)
    if factors is None:
        raise HTTPException(
            status_code=422, detail="Not enough ratings yet — rate a few more items first."
        )
    return factors


@router.post("/train", response_model=ModelRunOut)
def train(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        model_run = model_service.train_model(db)
    except model_service.NotEnoughRatingsError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return ModelRunOut.model_validate(model_run)


@router.get("/status", response_model=ModelStatusOut)
def status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    last_run = model_service.get_latest_model_run(db)
    return ModelStatusOut(
        trained=last_run is not None,
        stale=model_service.is_stale(db),
        min_ratings_required=MIN_RATINGS_FOR_TRAIN,
        current_rating_count=db.query(Rating).count(),
        last_run=ModelRunOut.model_validate(last_run) if last_run else None,
    )


@router.get("/factors", response_model=FactorsOut)
def factors(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = _factors_or_422(db)
    model_run = data["model_run"]

    items_out = []
    for item_id, factor in data["items"].items():
        item = db.get(Item, item_id)
        if item is None:
            continue
        items_out.append(
            FactorItemOut(
                item_id=item_id,
                title=item.title,
                show_title=item.show_title,
                type=item.type,
                season_number=item.season_number,
                vector=factor["vector"],
                bias=factor["bias"],
            )
        )

    users_out = []
    for user_id, factor in data["users"].items():
        user = db.get(User, user_id)
        if user is None:
            continue
        users_out.append(
            FactorUserOut(user_id=user_id, name=user.name, vector=factor["vector"], bias=factor["bias"])
        )

    return FactorsOut(k=model_run.k, global_mean=model_run.global_mean, items=items_out, users=users_out)


@router.get("/factors/{factor_index}/top-items", response_model=FactorTopItemsOut)
def factor_top_items(
    factor_index: int,
    n: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = _factors_or_422(db)
    model_run = data["model_run"]
    if not (0 <= factor_index < model_run.k):
        raise HTTPException(
            status_code=400, detail=f"factor_index must be between 0 and {model_run.k - 1}"
        )

    loadings = []
    for item_id, factor in data["items"].items():
        item = db.get(Item, item_id)
        if item is None:
            continue
        loadings.append(
            FactorLoadingOut(
                item_id=item_id,
                title=item.title,
                show_title=item.show_title,
                loading=factor["vector"][factor_index],
            )
        )

    loadings.sort(key=lambda x: x.loading, reverse=True)
    return FactorTopItemsOut(
        factor_index=factor_index, top=loadings[:n], bottom=list(reversed(loadings[-n:]))
    )
