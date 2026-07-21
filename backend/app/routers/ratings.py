from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.item import Item
from app.models.rating import Rating
from app.models.user import User
from app.schemas.rating import RatingOut, RatingUpsert
from app.services import library_service, model_service

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


def _retrain_if_possible(db: Session) -> None:
    """Retrain synchronously after every rating write. At this scale (a handful of users,
    dozens of ratings, k<=6) training takes well under 100ms, so a background task queue would
    be unjustified complexity - see the plan's risk notes on SQLite concurrency at this scale."""
    try:
        model_service.train_model(db)
    except model_service.NotEnoughRatingsError:
        pass


def _rating_to_out(rating: Rating, item: Item) -> RatingOut:
    return RatingOut(
        id=rating.id,
        user_id=rating.user_id,
        item_id=rating.item_id,
        rating=rating.rating,
        rated_at=rating.rated_at,
        item_title=item.title,
        item_show_title=item.show_title,
        item_type=item.type,
        item_season_number=item.season_number,
    )


@router.get("/me", response_model=list[RatingOut])
def my_ratings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(Rating, Item)
        .join(Item, Rating.item_id == Item.id)
        .filter(Rating.user_id == current_user.id)
        .all()
    )
    return [_rating_to_out(r, i) for r, i in rows]


@router.get("/all", response_model=list[RatingOut])
def all_ratings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Rating, Item).join(Item, Rating.item_id == Item.id).all()
    return [_rating_to_out(r, i) for r, i in rows]


@router.post("", response_model=RatingOut)
def upsert_rating(
    payload: RatingUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(Item, payload.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    rating = (
        db.query(Rating)
        .filter(Rating.user_id == current_user.id, Rating.item_id == payload.item_id)
        .first()
    )
    if rating is None:
        rating = Rating(user_id=current_user.id, item_id=payload.item_id, rating=payload.rating)
        db.add(rating)
    else:
        rating.rating = payload.rating

    library_service.add_to_library(db, current_user.id, payload.item_id)
    db.commit()
    db.refresh(rating)
    _retrain_if_possible(db)
    return _rating_to_out(rating, item)


@router.patch("/{item_id}", response_model=RatingOut)
def update_rating(
    item_id: int,
    payload: RatingUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.item_id != item_id:
        raise HTTPException(status_code=400, detail="item_id mismatch")
    return upsert_rating(payload, db, current_user)


@router.delete("/{item_id}", status_code=204)
def delete_rating(
    item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    rating = (
        db.query(Rating)
        .filter(Rating.user_id == current_user.id, Rating.item_id == item_id)
        .first()
    )
    if rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    db.delete(rating)
    db.commit()
    _retrain_if_possible(db)
