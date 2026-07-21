from sqlalchemy.orm import Session

from app.models.rating import Rating
from app.services import model_service
from app.services.similarity_service import cosine_similarity

HIGH_RATING_THRESHOLD = 4
TOP_N_REASONS = 2


def generate_explanation(db: Session, factors: dict, user_id: int, item_id: int) -> str:
    item_factor = factors["items"].get(item_id)
    if item_factor is None:
        return "This item hasn't been rated by anyone yet, so this is just an overall guess."

    user_high_ratings = (
        db.query(Rating)
        .filter(Rating.user_id == user_id, Rating.rating >= HIGH_RATING_THRESHOLD)
        .all()
    )
    if not user_high_ratings:
        if db.query(Rating).filter(Rating.user_id == user_id).count() == 0:
            return "You haven't rated anything yet, so this is ranked by overall popularity."
        return "Based on your overall taste profile so far."

    item_vector = item_factor["vector"]
    scored = []
    for r in user_high_ratings:
        neighbor_factor = factors["items"].get(r.item_id)
        if neighbor_factor is None or r.item_id == item_id:
            continue
        sim = cosine_similarity(item_vector, neighbor_factor["vector"])
        scored.append((r.item_id, sim))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    top = [pair for pair in scored[:TOP_N_REASONS] if pair[1] > 0]

    if not top:
        return "Based on your overall taste profile so far."

    titles = [model_service.item_display_title(db, iid) for iid, _sim in top]
    joined = " and ".join(titles) if len(titles) < 3 else ", ".join(titles[:-1]) + f", and {titles[-1]}"
    return f"Similar latent profile to {joined}, which you rated highly."
