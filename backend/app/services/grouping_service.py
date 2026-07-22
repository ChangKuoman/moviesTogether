import json
from datetime import datetime
from itertools import groupby

from app.models.item import Item
from app.schemas.item import ItemOut, ShowGroupOut


def item_to_out(item: Item, added_at: datetime | None = None) -> ItemOut:
    return ItemOut(
        id=item.id,
        title=item.title,
        type=item.type,
        season_number=item.season_number,
        show_title=item.show_title,
        year=item.year,
        tmdb_id=item.tmdb_id,
        genres=json.loads(item.genres) if item.genres else None,
        overview=item.overview,
        poster_url=item.poster_url,
        director=item.director,
        cast=json.loads(item.cast) if item.cast else None,
        runtime=item.runtime,
        source=item.source,
        created_at=item.created_at,
        added_at=added_at,
    )


def group_by_show(rows: list[tuple[Item, datetime | None]]) -> list[ShowGroupOut]:
    ordered = sorted(rows, key=lambda r: (r[0].show_title, r[0].season_number or 0))
    groups = []
    for show_title, group_rows in groupby(ordered, key=lambda r: r[0].show_title):
        items = [item_to_out(item, added_at) for item, added_at in group_rows]
        groups.append(ShowGroupOut(show_title=show_title, items=items))
    return sorted(groups, key=lambda g: g.show_title)
