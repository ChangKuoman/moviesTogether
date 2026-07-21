import json

from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_LR, DEFAULT_REG, MIN_RATINGS_FOR_TRAIN
from app.models.factor import ItemFactor, ModelRun, UserFactor
from app.models.item import Item
from app.models.rating import Rating
from app.models.user import User
from app.services.mf_service import MatrixFactorization, compute_k


class NotEnoughRatingsError(Exception):
    pass


def train_model(db: Session) -> ModelRun:
    ratings = db.query(Rating).all()
    if len(ratings) < MIN_RATINGS_FOR_TRAIN:
        raise NotEnoughRatingsError(
            f"Need at least {MIN_RATINGS_FOR_TRAIN} ratings to train, have {len(ratings)}"
        )

    user_ids = sorted({r.user_id for r in ratings})
    item_ids = sorted({r.item_id for r in ratings})
    user_idx = {uid: idx for idx, uid in enumerate(user_ids)}
    item_idx = {iid: idx for idx, iid in enumerate(item_ids)}

    triples = [(user_idx[r.user_id], item_idx[r.item_id], float(r.rating)) for r in ratings]

    k = compute_k(len(triples), len(item_ids))
    mf = MatrixFactorization(
        n_users=len(user_ids), n_items=len(item_ids), k=k, lr=DEFAULT_LR, reg=DEFAULT_REG
    )
    result = mf.fit(triples)

    model_run = ModelRun(
        k=k,
        epochs_run=result["epochs_run"],
        final_train_rmse=result["final_rmse"],
        n_ratings_used=len(triples),
        lr=DEFAULT_LR,
        reg=DEFAULT_REG,
        global_mean=mf.global_mean,
    )
    db.add(model_run)
    db.flush()  # need model_run.id for the factor rows below

    for uid in user_ids:
        idx = user_idx[uid]
        db.add(
            UserFactor(
                model_run_id=model_run.id,
                user_id=uid,
                vector_json=json.dumps(mf.P[idx].tolist()),
                bias=float(mf.b_u[idx]),
            )
        )
    for iid in item_ids:
        idx = item_idx[iid]
        db.add(
            ItemFactor(
                model_run_id=model_run.id,
                item_id=iid,
                vector_json=json.dumps(mf.Q[idx].tolist()),
                bias=float(mf.b_i[idx]),
            )
        )

    db.commit()
    db.refresh(model_run)
    return model_run


def get_latest_model_run(db: Session) -> ModelRun | None:
    return db.query(ModelRun).order_by(ModelRun.id.desc()).first()


def load_latest_factors(db: Session) -> dict | None:
    """Returns None if the model has never been trained. Otherwise:
    {
        "model_run": ModelRun,
        "users": {user_id: {"vector": list[float], "bias": float}},
        "items": {item_id: {"vector": list[float], "bias": float}},
    }
    """
    model_run = get_latest_model_run(db)
    if model_run is None:
        return None

    user_factors = db.query(UserFactor).filter(UserFactor.model_run_id == model_run.id).all()
    item_factors = db.query(ItemFactor).filter(ItemFactor.model_run_id == model_run.id).all()

    return {
        "model_run": model_run,
        "users": {
            uf.user_id: {"vector": json.loads(uf.vector_json), "bias": uf.bias}
            for uf in user_factors
        },
        "items": {
            itf.item_id: {"vector": json.loads(itf.vector_json), "bias": itf.bias}
            for itf in item_factors
        },
    }


def predict_rating(factors: dict, user_id: int, item_id: int) -> float:
    """Predicts a rating from a loaded factors snapshot (see load_latest_factors). Falls back to
    global_mean + item_bias (a popularity-based estimate) if the user has never rated anything and
    so has no learned P_u - this is the "new user" cold start case, see the plan's risk notes."""
    global_mean = factors["model_run"].global_mean
    user = factors["users"].get(user_id)
    item = factors["items"].get(item_id)

    b_u = user["bias"] if user else 0.0
    b_i = item["bias"] if item else 0.0
    dot = 0.0
    if user and item:
        dot = sum(p * q for p, q in zip(user["vector"], item["vector"]))

    return global_mean + b_u + b_i + dot


def is_stale(db: Session) -> bool:
    """True if ratings have changed since the last trained model_run (naive but sufficient at this
    scale: compares total rating count, since we always retrain synchronously after each rating write
    anyway - this is mainly a signal for the UI, not a correctness guarantee)."""
    model_run = get_latest_model_run(db)
    if model_run is None:
        return db.query(Rating).count() >= MIN_RATINGS_FOR_TRAIN
    return db.query(Rating).count() != model_run.n_ratings_used


def user_display_name(db: Session, user_id: int) -> str:
    user = db.get(User, user_id)
    return user.name if user else "?"


def item_display_title(db: Session, item_id: int) -> str:
    item = db.get(Item, item_id)
    if item is None:
        return "?"
    return f"{item.title} S{item.season_number}" if item.type == "season" else item.title
