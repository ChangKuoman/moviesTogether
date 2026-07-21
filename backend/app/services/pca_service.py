import numpy as np
from sklearn.decomposition import PCA

MIN_ITEMS_HARD_FLOOR = 3
MIN_ITEMS_FOR_RELIABLE_MAP = 10


class InsufficientDataError(Exception):
    pass


def _pad_to_2d(coords: np.ndarray) -> np.ndarray:
    if coords.shape[1] == 1:
        return np.hstack([coords, np.zeros((coords.shape[0], 1))])
    return coords


def fit_movie_map(item_vectors: np.ndarray) -> tuple[PCA, np.ndarray, list[float], str | None]:
    """Fits PCA on item latent vectors (this defines the map's 2D basis).

    Returns (fitted pca, item coords shape (n_items, 2), explained_variance_ratio, warning|None).
    Raises InsufficientDataError below a hard floor of items - a "map" of 1-2 points is meaningless.
    Below MIN_ITEMS_FOR_RELIABLE_MAP, returns a warning instead of failing; the map still renders,
    it's just flagged as not trustworthy yet.
    """
    n_items, k = item_vectors.shape
    if n_items < MIN_ITEMS_HARD_FLOOR:
        raise InsufficientDataError(
            f"Need at least {MIN_ITEMS_HARD_FLOOR} rated items for a meaningful map, have {n_items}"
        )

    n_components = min(2, k, n_items - 1)
    pca = PCA(n_components=n_components)
    coords = _pad_to_2d(pca.fit_transform(item_vectors))

    explained = pca.explained_variance_ratio_.tolist()
    if len(explained) == 1:
        explained.append(0.0)

    warning = None
    if n_items < MIN_ITEMS_FOR_RELIABLE_MAP:
        warning = f"Only {n_items} rated items so far — add more ratings for a more meaningful map."

    return pca, coords, explained, warning


def project(pca: PCA, vectors: np.ndarray) -> np.ndarray:
    """Projects extra vectors (e.g. user vectors) into an already-fitted map's 2D basis, so points
    from different sources land on the same map consistently."""
    return _pad_to_2d(pca.transform(vectors))
