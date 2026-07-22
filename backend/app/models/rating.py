from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_rating_user_item"),
        # rating * 2 must be a whole number so only half-star increments (0.5, 1.0, 1.5, ..., 5.0)
        # are ever stored - see app/services/migrations.py for how this replaced the older
        # whole-star-only (1-5) constraint on an already-deployed database.
        CheckConstraint(
            "rating >= 0.5 AND rating <= 5 AND CAST(rating * 2 AS INTEGER) = rating * 2",
            name="ck_rating_range",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    rating: Mapped[float] = mapped_column(Float)
    rated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
