import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.item import Item
from app.models.user import User
from app.schemas.recommend import MapPointOut, MapUserPointOut, MovieMapOut, NeighborOut
from app.services import friendship_service, model_service, pca_service
from app.services.grouping_service import item_to_out
from app.services.similarity_service import nearest_neighbors

router = APIRouter(prefix="/api/movie-map", tags=["movie-map"])


def _factors_or_422(db: Session) -> dict:
    factors = model_service.load_latest_factors(db)
    if factors is None:
        raise HTTPException(
            status_code=422, detail="Not enough ratings yet — rate a few more items first."
        )
    return factors


@router.get("", response_model=MovieMapOut)
def movie_map(
    scope: str = "friends",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """scope='friends' shows only you + your accepted friends, with real names. scope='everyone'
    shows every user who has rated something (for context on where the whole userbase's taste
    sits), but only your own point keeps its real name - everyone else is anonymized, both the
    name and the id (a synthetic negative id, so it can't be cross-referenced against any other
    endpoint) - since unlike friends, you haven't agreed to be identifiable to these people."""
    if scope not in ("friends", "everyone"):
        raise HTTPException(status_code=400, detail="scope must be 'friends' or 'everyone'")

    data = _factors_or_422(db)

    item_ids = list(data["items"].keys())
    item_vectors = np.array([data["items"][iid]["vector"] for iid in item_ids])

    try:
        pca, coords, explained, warning = pca_service.fit_movie_map(item_vectors)
    except pca_service.InsufficientDataError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    points = []
    for idx, item_id in enumerate(item_ids):
        item = db.get(Item, item_id)
        if item is None:
            continue
        item_out = item_to_out(item)
        points.append(
            MapPointOut(
                item_id=item_id,
                title=item.title,
                show_title=item.show_title,
                type=item.type,
                season_number=item.season_number,
                x=float(coords[idx, 0]),
                y=float(coords[idx, 1]),
                genres=item_out.genres,
                poster_url=item_out.poster_url,
            )
        )

    if scope == "friends":
        visible_ids = {current_user.id} | {f.id for f in friendship_service.list_friends(db, current_user.id)}
    else:
        visible_ids = set(data["users"].keys())

    user_points = []
    user_ids = [uid for uid in data["users"].keys() if uid in visible_ids]
    if user_ids:
        user_vectors = np.array([data["users"][uid]["vector"] for uid in user_ids])
        user_coords = pca_service.project(pca, user_vectors)
        anon_counter = 0
        for idx, user_id in enumerate(user_ids):
            is_self = user_id == current_user.id
            if scope == "everyone" and not is_self:
                anon_counter -= 1
                out_id, out_name = anon_counter, "Anonymous"
            else:
                user = db.get(User, user_id)
                if user is None:
                    continue
                out_id, out_name = user_id, user.name
            user_points.append(
                MapUserPointOut(
                    user_id=out_id,
                    name=out_name,
                    x=float(user_coords[idx, 0]),
                    y=float(user_coords[idx, 1]),
                )
            )

    return MovieMapOut(
        points=points,
        user_points=user_points,
        explained_variance=explained,
        n_components=coords.shape[1],
        warning=warning,
    )


@router.get("/neighbors/{item_id}", response_model=list[NeighborOut])
def movie_map_neighbors(
    item_id: int,
    n: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = _factors_or_422(db)
    target = data["items"].get(item_id)
    if target is None:
        raise HTTPException(status_code=404, detail="This item has no trained latent vector yet")

    candidates = {iid: f["vector"] for iid, f in data["items"].items()}
    neighbors = nearest_neighbors(target["vector"], candidates, n=n, exclude_id=item_id)

    out = []
    for neighbor_id, similarity in neighbors:
        item = db.get(Item, neighbor_id)
        if item is None:
            continue
        out.append(
            NeighborOut(
                item_id=neighbor_id,
                title=item.title,
                show_title=item.show_title,
                similarity=round(similarity, 3),
            )
        )
    return out
