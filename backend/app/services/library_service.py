from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.library_entry import LibraryEntry
from app.models.rating import Rating


def is_in_library(db: Session, user_id: int, item_id: int) -> bool:
    return (
        db.query(LibraryEntry).filter_by(user_id=user_id, item_id=item_id).first() is not None
    )


def add_to_library(db: Session, user_id: int, item_id: int) -> LibraryEntry:
    """Idempotent: returns the existing entry if the item is already in this user's library."""
    entry = db.query(LibraryEntry).filter_by(user_id=user_id, item_id=item_id).first()
    if entry is None:
        entry = LibraryEntry(user_id=user_id, item_id=item_id)
        db.add(entry)
        db.flush()
    return entry


def remove_from_library(db: Session, user_id: int, item_id: int) -> None:
    """Removes the item from this user's library and clears their rating on it. If no other
    user still has it in their library or rated it, the underlying Item is deleted too."""
    db.query(LibraryEntry).filter_by(user_id=user_id, item_id=item_id).delete()
    db.query(Rating).filter_by(user_id=user_id, item_id=item_id).delete()
    db.flush()

    still_referenced = (
        db.query(LibraryEntry).filter_by(item_id=item_id).first() is not None
        or db.query(Rating).filter_by(item_id=item_id).first() is not None
    )
    if not still_referenced:
        item = db.get(Item, item_id)
        if item is not None:
            db.delete(item)
