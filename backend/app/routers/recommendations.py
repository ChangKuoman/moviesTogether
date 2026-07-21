from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.item import Item
from app.models.library_entry import LibraryEntry
from app.models.rating import Rating
from app.models.user import User
from app.schemas.recommend import ExplanationOut, RecommendationOut
from app.services import confidence_service, explanation_service, model_service

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


def _load_factors_or_422(db: Session) -> dict:
    factors = model_service.load_latest_factors(db)
    if factors is None:
        raise HTTPException(
            status_code=422, detail="Not enough ratings yet — rate a few more items first."
        )
    return factors


def _build_recommendation(db: Session, factors: dict, user_id: int, item: Item) -> RecommendationOut:
    predicted = max(1.0, min(5.0, model_service.predict_rating(factors, user_id, item.id)))
    confidence = confidence_service.compute_confidence(db, factors, user_id, item.id)
    explanation = explanation_service.generate_explanation(db, factors, user_id, item.id)
    return RecommendationOut(
        item_id=item.id,
        title=item.title,
        show_title=item.show_title,
        type=item.type,
        season_number=item.season_number,
        predicted_rating=round(predicted, 2),
        confidence=confidence["score"],
        confidence_label=confidence["label"],
        confidence_reason=confidence["reason"],
        explanation=explanation,
    )


@router.get("/me", response_model=list[RecommendationOut])
def my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    factors = _load_factors_or_422(db)

    rated_item_ids = {
        r.item_id for r in db.query(Rating).filter(Rating.user_id == current_user.id).all()
    }
    library_item_ids = {
        le.item_id
        for le in db.query(LibraryEntry).filter(LibraryEntry.user_id == current_user.id).all()
    }
    unseen_item_ids = library_item_ids - rated_item_ids
    unseen_items = db.query(Item).filter(Item.id.in_(unseen_item_ids)).all() if unseen_item_ids else []

    recommendations = [
        _build_recommendation(db, factors, current_user.id, item) for item in unseen_items
    ]
    recommendations.sort(key=lambda r: r.predicted_rating, reverse=True)
    return recommendations


@router.get("/{item_id}/explain", response_model=ExplanationOut)
def explain_recommendation(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    factors = _load_factors_or_422(db)
    rec = _build_recommendation(db, factors, current_user.id, item)
    return ExplanationOut(
        item_id=rec.item_id,
        predicted_rating=rec.predicted_rating,
        confidence=rec.confidence,
        confidence_label=rec.confidence_label,
        confidence_reason=rec.confidence_reason,
        explanation=rec.explanation,
    )
