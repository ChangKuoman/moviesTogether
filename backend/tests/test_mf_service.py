import numpy as np

from app.services.mf_service import MatrixFactorization, compute_k


def _synthetic_triples():
    # 2 users x 4 items, deliberately sparse (a few ratings missing) - mirrors real small-N usage.
    # user 0 likes items 0,1 and dislikes 2,3; user 1 is the opposite.
    ratings = {
        (0, 0): 5,
        (0, 1): 4,
        (0, 2): 1,
        (1, 1): 2,
        (1, 2): 5,
        (1, 3): 4,
    }
    return [(u, i, r) for (u, i), r in ratings.items()]


def test_fit_converges_and_reduces_rmse():
    triples = _synthetic_triples()
    mf = MatrixFactorization(n_users=2, n_items=4, k=2, lr=0.05, reg=0.05, epochs=300, seed=1)
    result = mf.fit(triples)

    assert result["epochs_run"] > 1
    assert len(result["history"]) == result["epochs_run"]
    # RMSE should have dropped substantially from the first epoch to the last.
    assert result["history"][-1] < result["history"][0]
    # and should have converged to something small on this easy synthetic case.
    assert result["final_rmse"] < 0.5


def test_vectors_stay_bounded_no_blowup():
    triples = _synthetic_triples()
    mf = MatrixFactorization(n_users=2, n_items=4, k=2, lr=0.05, reg=0.05, epochs=300, seed=1)
    mf.fit(triples)

    assert np.all(np.isfinite(mf.P))
    assert np.all(np.isfinite(mf.Q))
    assert np.linalg.norm(mf.P) < 50
    assert np.linalg.norm(mf.Q) < 50


def test_predict_matches_observed_ratings_reasonably_well():
    triples = _synthetic_triples()
    mf = MatrixFactorization(n_users=2, n_items=4, k=2, lr=0.05, reg=0.05, epochs=300, seed=1)
    mf.fit(triples)

    for u, i, r in triples:
        pred = mf.predict(u, i)
        assert abs(pred - r) < 1.5


def test_compute_k_scales_down_for_small_n():
    assert compute_k(n_ratings=6, n_items=4) <= 4
    assert compute_k(n_ratings=6, n_items=4) >= 1
    # plenty of data and items -> hits the MAX_K ceiling
    assert compute_k(n_ratings=1000, n_items=1000) == 6
    # degenerate single-item case should not crash and should return >= 1
    assert compute_k(n_ratings=4, n_items=1) >= 1
