from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LibraryEntry(Base):
    """Marks that an item is in a given user's personal library. The underlying Item row
    is shared (so ratings on the same title/tmdb_id can still be compared across users),
    but which items show up in whose Library tab is per-user."""

    __tablename__ = "library_entries"
    __table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_library_user_item"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
