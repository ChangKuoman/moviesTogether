from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.tmdb import TmdbSearchResultOut, TmdbSeasonOut, TmdbStatusOut
from app.services import tmdb_service

router = APIRouter(prefix="/api/tmdb", tags=["tmdb"])


@router.get("/status", response_model=TmdbStatusOut)
def status(current_user: User = Depends(get_current_user)):
    return TmdbStatusOut(configured=tmdb_service.is_configured())


@router.get("/search", response_model=list[TmdbSearchResultOut])
def search(
    q: str,
    type: str = "movie",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if type not in ("movie", "tv"):
        raise HTTPException(status_code=400, detail="type must be 'movie' or 'tv'")
    return tmdb_service.search(db, q, type)


@router.get("/tv/{tmdb_id}/seasons", response_model=list[TmdbSeasonOut])
def tv_seasons(tmdb_id: int, current_user: User = Depends(get_current_user)):
    return tmdb_service.get_tv_seasons(tmdb_id)
