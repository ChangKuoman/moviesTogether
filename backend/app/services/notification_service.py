from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.notification import Notification

MAX_NOTIFICATIONS_RETURNED = 50


def create_notification(db: Session, user_id: int, actor_id: int, type: str) -> None:
    db.add(Notification(user_id=user_id, actor_id=actor_id, type=type))


def list_notifications(db: Session, user_id: int) -> list[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(MAX_NOTIFICATIONS_RETURNED)
        .all()
    )


def unread_count(db: Session, user_id: int) -> int:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
        .count()
    )


def mark_all_read(db: Session, user_id: int) -> None:
    now = datetime.now(timezone.utc)
    (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read_at.is_(None))
        .update({"read_at": now})
    )
    db.commit()
