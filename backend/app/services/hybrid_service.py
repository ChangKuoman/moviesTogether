from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.rating import Rating
from app.services import content_service, model_service
from app.services.similarity_service import cosine_similarity

HIGH_RATING_THRESHOLD = 4


def compute_hybrid_recommendations(
    db: Session, factors: dict, user_id: int, w_collab: float, w_content: float
) -> list[dict]:
    """Blends the collaborative (matrix factorization) score with a content-based (genre overlap)
    score for each unseen item: hybrid = w_collab * collaborative + w_content * content, both
    normalized to 0-1 before blending, then mapped back to a 1-5 scale for display alongside the
    plain collaborative prediction.
    """
    all_items = db.query(Item).all()
    vocab = content_service.build_genre_vocab(all_items)
    content_vectors = {item.id: content_service.get_content_vector(item, vocab) for item in all_items}

    liked_item_ids = {
        r.item_id
        for r in db.query(Rating).filter(
            Rating.user_id == user_id, Rating.rating >= HIGH_RATING_THRESHOLD
        )
    }
    liked_content_vectors = [content_vectors[iid] for iid in liked_item_ids if iid in content_vectors]

    rated_item_ids = {r.item_id for r in db.query(Rating).filter(Rating.user_id == user_id)}
    unseen_items = [item for item in all_items if item.id not in rated_item_ids]

    results = []
    for item in unseen_items:
        collab_pred = max(1.0, min(5.0, model_service.predict_rating(factors, user_id, item.id)))
        collab_norm = (collab_pred - 1) / 4

        if liked_content_vectors:
            content_score = sum(
                cosine_similarity(content_vectors[item.id], v) for v in liked_content_vectors
            ) / len(liked_content_vectors)
        else:
            content_score = 0.0

        hybrid_norm = w_collab * collab_norm + w_content * content_score
        hybrid_rating = max(1.0, min(5.0, 1 + hybrid_norm * 4))

        results.append(
            {
                "item_id": item.id,
                "title": item.title,
                "show_title": item.show_title,
                "type": item.type,
                "season_number": item.season_number,
                "collaborative_score": round(collab_pred, 2),
                "content_score": round(content_score, 2),
                "hybrid_score": round(hybrid_rating, 2),
            }
        )

    results.sort(key=lambda r: r["hybrid_score"], reverse=True)
    return results
