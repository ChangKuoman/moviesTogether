import numpy as np


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    denom = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if denom < 1e-9:
        return 0.0
    return float(a_arr @ b_arr / denom)


def nearest_neighbors(
    target_vector: list[float],
    candidates: dict[int, list[float]],
    n: int = 5,
    exclude_id: int | None = None,
) -> list[tuple[int, float]]:
    """Returns up to n (id, similarity) pairs sorted by descending cosine similarity."""
    scored = [
        (cid, cosine_similarity(target_vector, vec))
        for cid, vec in candidates.items()
        if cid != exclude_id
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:n]
