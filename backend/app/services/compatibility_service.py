import json

from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.library_entry import LibraryEntry
from app.models.rating import Rating
from app.services import model_service
from app.services.similarity_service import cosine_similarity

TOP_N_AGREEMENTS = 5


class UsersNotComparableError(Exception):
    pass


def _overlapping_ratings(db: Session, user_a_id: int, user_b_id: int) -> list[tuple[Rating, Rating, Item]]:
    ratings_a = {r.item_id: r for r in db.query(Rating).filter(Rating.user_id == user_a_id)}
    ratings_b = {r.item_id: r for r in db.query(Rating).filter(Rating.user_id == user_b_id)}
    overlap_ids = set(ratings_a) & set(ratings_b)

    rows = []
    for item_id in overlap_ids:
        item = db.get(Item, item_id)
        if item is not None:
            rows.append((ratings_a[item_id], ratings_b[item_id], item))
    return rows


def compute_compatibility(db: Session, factors: dict, user_a_id: int, user_b_id: int) -> dict:
    user_a_factor = factors["users"].get(user_a_id)
    user_b_factor = factors["users"].get(user_b_id)
    if user_a_factor is None or user_b_factor is None:
        raise UsersNotComparableError("Both users need at least one rating to compute compatibility")

    similarity = cosine_similarity(user_a_factor["vector"], user_b_factor["vector"])
    score_pct = round((similarity + 1) / 2 * 100, 1)

    overlap = _overlapping_ratings(db, user_a_id, user_b_id)
    scored = [
        {
            "item_id": item.id,
            "title": item.title,
            "show_title": item.show_title,
            "user_a_rating": ra.rating,
            "user_b_rating": rb.rating,
            "diff": abs(ra.rating - rb.rating),
        }
        for ra, rb, item in overlap
    ]

    agreements = sorted(scored, key=lambda x: (x["diff"], -(x["user_a_rating"] + x["user_b_rating"])))
    disagreements = sorted(scored, key=lambda x: -x["diff"])

    genre_breakdown = _genre_breakdown(overlap)

    return {
        "score_pct": score_pct,
        "overlap_count": len(overlap),
        "top_agreements": agreements[:TOP_N_AGREEMENTS],
        "top_disagreements": disagreements[:TOP_N_AGREEMENTS],
        "genre_breakdown": genre_breakdown,
    }


def compute_watch_together(db: Session, factors: dict, user_a_id: int, user_b_id: int) -> list[dict]:
    """Ranks candidate items by how good a joint pick they'd be. A candidate is anything either
    of you has saved to your library that you haven't BOTH already rated - if only one of you
    has rated it, it's still a valid "what to watch together" pick (flagged via rated_by_a/
    rated_by_b so the caller can split into "neither watched" / "you watched" / "friend watched"
    sections). Uses the 'least misery' strategy from group recommendation: score =
    min(predicted_a, predicted_b), so a title one of you would love but the other would hate
    can't outrank something you'd both enjoy solidly. Predictions fall back to global_mean + bias
    for a user with no ratings yet (see model_service.predict_rating), so this still works right
    after a friendship forms. Returns every candidate (not just a top-N) since callers bucket by
    section before displaying.
    """
    rated_a = {r.item_id for r in db.query(Rating).filter(Rating.user_id == user_a_id)}
    rated_b = {r.item_id for r in db.query(Rating).filter(Rating.user_id == user_b_id)}
    rated_by_both = rated_a & rated_b

    library_a = {le.item_id for le in db.query(LibraryEntry).filter(LibraryEntry.user_id == user_a_id)}
    library_b = {le.item_id for le in db.query(LibraryEntry).filter(LibraryEntry.user_id == user_b_id)}
    candidate_ids = (library_a | library_b) - rated_by_both

    if not candidate_ids:
        return []
    candidates = db.query(Item).filter(Item.id.in_(candidate_ids))

    results = []
    for item in candidates.all():
        predicted_a = round(max(1.0, min(5.0, model_service.predict_rating(factors, user_a_id, item.id))), 2)
        predicted_b = round(max(1.0, min(5.0, model_service.predict_rating(factors, user_b_id, item.id))), 2)
        results.append(
            {
                "item_id": item.id,
                "title": item.title,
                "show_title": item.show_title,
                "type": item.type,
                "season_number": item.season_number,
                "predicted_a": predicted_a,
                "predicted_b": predicted_b,
                "watch_together_score": round(min(predicted_a, predicted_b), 2),
                "rated_by_a": item.id in rated_a,
                "rated_by_b": item.id in rated_b,
            }
        )

    results.sort(key=lambda r: r["watch_together_score"], reverse=True)
    return results


def _genre_breakdown(overlap: list[tuple[Rating, Rating, Item]]) -> list[dict]:
    per_genre: dict[str, list[tuple[int, int]]] = {}
    for ra, rb, item in overlap:
        if not item.genres:
            continue
        for genre in json.loads(item.genres):
            per_genre.setdefault(genre, []).append((ra.rating, rb.rating))

    breakdown = []
    for genre, pairs in per_genre.items():
        a_avg = sum(p[0] for p in pairs) / len(pairs)
        b_avg = sum(p[1] for p in pairs) / len(pairs)
        breakdown.append({"genre": genre, "user_a_avg": round(a_avg, 2), "user_b_avg": round(b_avg, 2)})

    return sorted(breakdown, key=lambda x: x["genre"])
