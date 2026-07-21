import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.item import Item
from app.models.library_entry import LibraryEntry
from app.models.user import User
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate, ShowGroupOut
from app.schemas.tmdb import ItemFromTmdbCreate
from app.services import library_service, model_service, tmdb_service
from app.services.grouping_service import group_by_show, item_to_out

router = APIRouter(prefix="/api/items", tags=["items"])


def _retrain_if_possible(db: Session) -> None:
    try:
        model_service.train_model(db)
    except model_service.NotEnoughRatingsError:
        pass


def _my_items_query(db: Session, user_id: int):
    return db.query(Item).join(LibraryEntry, LibraryEntry.item_id == Item.id).filter(
        LibraryEntry.user_id == user_id
    )


@router.get("", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = _my_items_query(db, current_user.id).order_by(Item.show_title, Item.season_number).all()
    return [item_to_out(i) for i in items]


@router.get("/grouped", response_model=list[ShowGroupOut])
def list_items_grouped(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = _my_items_query(db, current_user.id).all()
    return group_by_show(items)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_to_out(item)


@router.post("", response_model=ItemOut, status_code=201)
def create_item(
    payload: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    item = (
        db.query(Item)
        .filter(
            Item.title == payload.title,
            Item.type == payload.type,
            Item.season_number == payload.season_number,
        )
        .first()
    )

    if item is not None:
        if library_service.is_in_library(db, current_user.id, item.id):
            raise HTTPException(status_code=400, detail="This is already in your library")
    else:
        item = Item(
            title=payload.title,
            type=payload.type,
            season_number=payload.season_number,
            show_title=payload.title,
            year=payload.year,
            source="manual",
        )
        db.add(item)
        db.flush()

    library_service.add_to_library(db, current_user.id, item.id)
    db.commit()
    db.refresh(item)
    return item_to_out(item)


@router.post("/from-tmdb", response_model=ItemOut, status_code=201)
def create_item_from_tmdb(
    payload: ItemFromTmdbCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.media_type not in ("movie", "tv"):
        raise HTTPException(status_code=400, detail="media_type must be 'movie' or 'tv'")
    if payload.media_type == "tv" and payload.season_number is None:
        raise HTTPException(status_code=400, detail="season_number is required for TV shows")

    item = (
        db.query(Item)
        .filter(Item.tmdb_id == payload.tmdb_id, Item.season_number == payload.season_number)
        .first()
    )

    if item is not None:
        if library_service.is_in_library(db, current_user.id, item.id):
            raise HTTPException(status_code=400, detail="This is already in your library")
    else:
        if payload.media_type == "movie":
            data = tmdb_service.build_movie_item_data(payload.tmdb_id)
            item_type = "movie"
        else:
            data = tmdb_service.build_season_item_data(payload.tmdb_id, payload.season_number)
            item_type = "season"

        if data is None:
            raise HTTPException(status_code=502, detail="Could not fetch details from TMDb")

        item = Item(
            title=data["title"],
            type=item_type,
            season_number=payload.season_number,
            show_title=data["title"],
            year=int(data["year"]) if data.get("year") else None,
            tmdb_id=payload.tmdb_id,
            genres=json.dumps(data["genres"]) if data.get("genres") else None,
            overview=data.get("overview"),
            poster_url=data.get("poster_url"),
            director=data.get("director"),
            cast=json.dumps(data["cast"]) if data.get("cast") else None,
            runtime=data.get("runtime"),
            source="tmdb",
        )
        db.add(item)
        db.flush()

    library_service.add_to_library(db, current_user.id, item.id)
    db.commit()
    db.refresh(item)
    return item_to_out(item)


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if not library_service.is_in_library(db, current_user.id, item_id):
        raise HTTPException(status_code=403, detail="This item isn't in your library")

    data = payload.model_dump(exclude_unset=True)
    if "genres" in data:
        genres = data.pop("genres")
        item.genres = json.dumps(genres) if genres is not None else None
    for field, value in data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item_to_out(item)


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if not library_service.is_in_library(db, current_user.id, item_id):
        raise HTTPException(status_code=404, detail="This item isn't in your library")

    library_service.remove_from_library(db, current_user.id, item_id)
    db.commit()
    _retrain_if_possible(db)
