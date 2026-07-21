import json
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.tmdb_cache import TmdbSearchCache

TMDB_BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w342"
CACHE_TTL = timedelta(days=30)


def is_configured() -> bool:
    return settings.tmdb_configured


def _poster_url(path: str | None) -> str | None:
    return f"{IMAGE_BASE_URL}{path}" if path else None


def _get(path: str, params: dict | None = None) -> dict | None:
    if not is_configured():
        return None
    try:
        response = httpx.get(
            f"{TMDB_BASE_URL}{path}",
            params={"api_key": settings.tmdb_api_key, **(params or {})},
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError:
        return None


def search(db: Session, query: str, media_type: str) -> list[dict]:
    """Search TMDb for movies or TV shows, caching results. Returns [] if not configured or on failure."""
    if not is_configured() or not query.strip():
        return []

    cached = (
        db.query(TmdbSearchCache)
        .filter(TmdbSearchCache.query == query, TmdbSearchCache.media_type == media_type)
        .first()
    )
    if cached and datetime.now(timezone.utc) - cached.fetched_at.replace(tzinfo=timezone.utc) < CACHE_TTL:
        return json.loads(cached.response_json)

    data = _get(f"/search/{media_type}", {"query": query})
    if data is None:
        return json.loads(cached.response_json) if cached else []

    results = [
        {
            "tmdb_id": r["id"],
            "title": r.get("title") or r.get("name"),
            "year": (r.get("release_date") or r.get("first_air_date") or "")[:4] or None,
            "poster_url": _poster_url(r.get("poster_path")),
            "media_type": media_type,
        }
        for r in data.get("results", [])[:10]
    ]

    if cached:
        cached.response_json = json.dumps(results)
        cached.fetched_at = datetime.now(timezone.utc)
    else:
        db.add(
            TmdbSearchCache(
                query=query, media_type=media_type, response_json=json.dumps(results)
            )
        )
    db.commit()

    return results


def get_tv_seasons(tmdb_id: int) -> list[dict]:
    data = _get(f"/tv/{tmdb_id}")
    if data is None:
        return []
    return [
        {
            "season_number": s["season_number"],
            "name": s.get("name"),
            "air_date": s.get("air_date"),
            "episode_count": s.get("episode_count"),
        }
        for s in data.get("seasons", [])
        if s.get("season_number", 0) > 0
    ]


def build_movie_item_data(tmdb_id: int) -> dict | None:
    data = _get(f"/movie/{tmdb_id}", {"append_to_response": "credits"})
    if data is None:
        return None

    credits = data.get("credits", {})
    director = next(
        (c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"), None
    )
    cast = [c["name"] for c in credits.get("cast", [])[:5]]

    return {
        "title": data.get("title"),
        "year": (data.get("release_date") or "")[:4] or None,
        "tmdb_id": tmdb_id,
        "genres": [g["name"] for g in data.get("genres", [])],
        "overview": data.get("overview"),
        "poster_url": _poster_url(data.get("poster_path")),
        "director": director,
        "cast": cast,
        "runtime": data.get("runtime"),
    }


def build_season_item_data(tmdb_id: int, season_number: int) -> dict | None:
    show = _get(f"/tv/{tmdb_id}", {"append_to_response": "credits"})
    season = _get(f"/tv/{tmdb_id}/season/{season_number}")
    if show is None or season is None:
        return None

    credits = show.get("credits", {})
    cast = [c["name"] for c in credits.get("cast", [])[:5]]
    episode_runtimes = show.get("episode_run_time") or []

    return {
        "title": show.get("name"),
        "year": (season.get("air_date") or "")[:4] or None,
        "tmdb_id": tmdb_id,
        "genres": [g["name"] for g in show.get("genres", [])],
        "overview": season.get("overview") or show.get("overview"),
        "poster_url": _poster_url(season.get("poster_path") or show.get("poster_path")),
        "director": None,
        "cast": cast,
        "runtime": episode_runtimes[0] if episode_runtimes else None,
    }
