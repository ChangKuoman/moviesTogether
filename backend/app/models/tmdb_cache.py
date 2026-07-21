from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TmdbSearchCache(Base):
    __tablename__ = "tmdb_search_cache"
    __table_args__ = (UniqueConstraint("query", "media_type", name="uq_tmdb_cache_query_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(String(255), index=True)
    media_type: Mapped[str] = mapped_column(Enum("movie", "tv", name="tmdb_media_type"))
    response_json: Mapped[str] = mapped_column(Text)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
