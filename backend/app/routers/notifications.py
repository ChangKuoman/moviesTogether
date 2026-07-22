from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import UserOut
from app.schemas.notification import NotificationOut
from app.services import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notifications = notification_service.list_notifications(db, current_user.id)
    actors = {a.id: a for a in db.query(User).filter(User.id.in_({n.actor_id for n in notifications}))}
    return [
        NotificationOut(
            id=n.id,
            type=n.type,
            actor=UserOut.model_validate(actors[n.actor_id]),
            created_at=n.created_at,
            read=n.read_at is not None,
        )
        for n in notifications
    ]


@router.get("/unread-count")
def get_unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"count": notification_service.unread_count(db, current_user.id)}


@router.post("/read")
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notification_service.mark_all_read(db, current_user.id)
    return {"status": "ok"}
