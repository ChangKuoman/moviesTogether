from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    trained_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    k: Mapped[int] = mapped_column(Integer)
    epochs_run: Mapped[int] = mapped_column(Integer)
    final_train_rmse: Mapped[float] = mapped_column(Float)
    n_ratings_used: Mapped[int] = mapped_column(Integer)
    lr: Mapped[float] = mapped_column(Float)
    reg: Mapped[float] = mapped_column(Float)
    global_mean: Mapped[float] = mapped_column(Float)


class UserFactor(Base):
    __tablename__ = "user_factors"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_run_id: Mapped[int] = mapped_column(ForeignKey("model_runs.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    vector_json: Mapped[str] = mapped_column(Text)  # JSON list[float], length k
    bias: Mapped[float] = mapped_column(Float)


class ItemFactor(Base):
    __tablename__ = "item_factors"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_run_id: Mapped[int] = mapped_column(ForeignKey("model_runs.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    vector_json: Mapped[str] = mapped_column(Text)
    bias: Mapped[float] = mapped_column(Float)
