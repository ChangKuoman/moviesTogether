import json
from itertools import groupby

from app.models.item import Item
from app.schemas.item import ItemOut, ShowGroupOut


def item_to_out(item: Item) -> ItemOut:
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
    )


def group_by_show(items: list[Item]) -> list[ShowGroupOut]:
    ordered = sorted(items, key=lambda i: (i.show_title, i.season_number or 0))
    groups = []
    for show_title, group_items in groupby(ordered, key=lambda i: i.show_title):
        groups.append(ShowGroupOut(show_title=show_title, items=[item_to_out(i) for i in group_items]))
    return sorted(groups, key=lambda g: g.show_title)
