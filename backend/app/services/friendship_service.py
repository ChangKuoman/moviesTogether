from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.friendship import Friendship
from app.models.user import User


def get_relationship(db: Session, user_a_id: int, user_b_id: int) -> Friendship | None:
    return (
        db.query(Friendship)
        .filter(
            or_(
                (Friendship.requester_id == user_a_id) & (Friendship.recipient_id == user_b_id),
                (Friendship.requester_id == user_b_id) & (Friendship.recipient_id == user_a_id),
            )
        )
        .first()
    )


def are_friends(db: Session, user_a_id: int, user_b_id: int) -> bool:
    relationship = get_relationship(db, user_a_id, user_b_id)
    return relationship is not None and relationship.status == "accepted"


def list_friends(db: Session, user_id: int) -> list[User]:
    accepted = (
        db.query(Friendship)
        .filter(
            Friendship.status == "accepted",
            or_(Friendship.requester_id == user_id, Friendship.recipient_id == user_id),
        )
        .all()
    )
    friend_ids = [
        f.recipient_id if f.requester_id == user_id else f.requester_id for f in accepted
    ]
    if not friend_ids:
        return []
    return db.query(User).filter(User.id.in_(friend_ids)).order_by(User.name).all()
