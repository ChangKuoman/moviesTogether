import numpy as np

from app.core.constants import (
    DEFAULT_LR,
    DEFAULT_REG,
    EARLY_STOP_MIN_DELTA,
    EARLY_STOP_PATIENCE,
    MAX_EPOCHS,
    MAX_K,
    MIN_K,
)


def compute_k(n_ratings: int, n_items: int) -> int:
    """Scale the latent dimensionality down for small-N data to avoid a degenerate factorization.

    Bounded by textbook MAX_K, by how much signal we actually have (n_ratings // 3),
    and by n_items - 1 so PCA/consumers downstream never see more dimensions than items.
    """
    upper_bound = max(1, n_items - 1)
    k = min(MAX_K, max(1, n_ratings // 3), upper_bound)
    if upper_bound >= MIN_K:
        k = max(MIN_K, k)
    return max(1, k)


class MatrixFactorization:
    """SGD-based matrix factorization with per-user/item bias terms, implemented from scratch.

    r_hat(u, i) = global_mean + b_u + b_i + P_u . Q_i
    """

    def __init__(
        self,
        n_users: int,
        n_items: int,
        k: int,
        lr: float = DEFAULT_LR,
        reg: float = DEFAULT_REG,
        epochs: int = MAX_EPOCHS,
        seed: int = 42,
    ):
        rng = np.random.default_rng(seed)
        self.rng = rng
        self.P = rng.normal(0, 0.05, size=(n_users, k))
        self.Q = rng.normal(0, 0.05, size=(n_items, k))
        self.b_u = np.zeros(n_users)
        self.b_i = np.zeros(n_items)
        self.global_mean = 0.0
        self.k = k
        self.lr = lr
        self.reg = reg
        self.epochs = epochs

    def fit(self, triples: list[tuple[int, int, float]]) -> dict:
        """triples: list of (user_idx, item_idx, rating). Trains on all data (see note in constants
        module) - there's no meaningful holdout split at N~10-20 ratings, so we rely on regularization
        and early stopping on training-RMSE plateau instead of a validation set.
        """
        ratings_arr = np.array([r for _, _, r in triples], dtype=float)
        self.global_mean = float(ratings_arr.mean())

        triples = list(triples)
        history = []
        best_rmse = float("inf")
        bad_epochs = 0
        epoch = 0

        for epoch in range(self.epochs):
            self.rng.shuffle(triples)
            sq_err_sum = 0.0

            for u, i, r in triples:
                pred = self.global_mean + self.b_u[u] + self.b_i[i] + self.P[u] @ self.Q[i]
                e = r - pred
                sq_err_sum += e**2

                self.b_u[u] += self.lr * (e - self.reg * self.b_u[u])
                self.b_i[i] += self.lr * (e - self.reg * self.b_i[i])

                p_u_old = self.P[u].copy()
                self.P[u] += self.lr * (e * self.Q[i] - self.reg * self.P[u])
                self.Q[i] += self.lr * (e * p_u_old - self.reg * self.Q[i])

            rmse = float(np.sqrt(sq_err_sum / len(triples)))
            history.append(rmse)

            if rmse < best_rmse - EARLY_STOP_MIN_DELTA:
                best_rmse, bad_epochs = rmse, 0
            else:
                bad_epochs += 1
            if bad_epochs >= EARLY_STOP_PATIENCE:
                break

        return {"final_rmse": history[-1], "epochs_run": epoch + 1, "history": history}

    def predict(self, u: int, i: int) -> float:
        return float(self.global_mean + self.b_u[u] + self.b_i[i] + self.P[u] @ self.Q[i])
