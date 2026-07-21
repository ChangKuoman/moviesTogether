import json

from app.models.item import Item

NO_GENRE_MARKER = "__no_genre__"


def build_genre_vocab(items: list[Item]) -> list[str]:
    genres = set()
    for item in items:
        if item.genres:
            genres.update(json.loads(item.genres))
    return sorted(genres) or [NO_GENRE_MARKER]


def get_content_vector(item: Item, vocab: list[str]) -> list[float]:
    """One-hot genre vector over the shared vocabulary. All-zero if the item has no genre data
    (e.g. manually-entered items without TMDb metadata) - cosine similarity against an all-zero
    vector is defined as 0 (see similarity_service), which is the honest answer: no content signal.

    This is deliberately v1-simple (no embeddings) - see the plan's note on deferring
    sentence-transformers to avoid a heavy model download for a personal, low-traffic app.
    """
    item_genres = set(json.loads(item.genres)) if item.genres else set()
    return [1.0 if g in item_genres else 0.0 for g in vocab]
