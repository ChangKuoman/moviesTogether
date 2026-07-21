from sqlalchemy.orm import Session

from app.models.rating import Rating
from app.services.similarity_service import cosine_similarity

SIMILARITY_THRESHOLD = 0.5
MAX_USER_RATINGS_FOR_FULL_CREDIT = 10
MAX_SIMILAR_RATED_FOR_FULL_CREDIT = 3


def compute_confidence(db: Session, factors: dict, user_id: int, item_id: int) -> dict:
    """A heuristic (not statistical/bootstrap) confidence score, appropriate for N~10-20 ratings
    where a real bootstrap-variance estimate would itself be noisy. Combines how much the target
    user has rated overall with how many of the item's nearest latent neighbors that user has
    already rated - i.e. "is this prediction backed by evidence, or mostly a cold guess."
    """
    user_factor = factors["users"].get(user_id)
    item_factor = factors["items"].get(item_id)

    n_user_ratings = db.query(Rating).filter(Rating.user_id == user_id).count()

    if user_factor is None or item_factor is None:
        return {
            "score": 0.05,
            "label": "low",
            "reason": "Not enough data yet for this user/item pair.",
        }

    user_rated_item_ids = {
        r.item_id for r in db.query(Rating).filter(Rating.user_id == user_id).all()
    }
    item_vector = item_factor["vector"]
    n_similar_rated = sum(
        1
        for iid, other in factors["items"].items()
        if iid in user_rated_item_ids
        and iid != item_id
        and cosine_similarity(item_vector, other["vector"]) >= SIMILARITY_THRESHOLD
    )

    rating_volume_score = min(n_user_ratings / MAX_USER_RATINGS_FOR_FULL_CREDIT, 1.0) * 0.5
    neighbor_evidence_score = (
        min(n_similar_rated / MAX_SIMILAR_RATED_FOR_FULL_CREDIT, 1.0) * 0.5
    )
    score = round(rating_volume_score + neighbor_evidence_score, 2)

    if score >= 0.66:
        label = "high"
    elif score >= 0.33:
        label = "medium"
    else:
        label = "low"

    reason = (
        f"Based on {n_user_ratings} rating(s) you've given and {n_similar_rated} "
        f"similar item(s) you've already rated."
    )
    return {"score": score, "label": label, "reason": reason}
