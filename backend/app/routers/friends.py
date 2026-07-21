from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.friendship import Friendship
from app.models.user import User
from app.schemas.auth import UserOut
from app.schemas.friendship import FriendRequestCreate, FriendRequestOut
from app.services import friendship_service

router = APIRouter(prefix="/api/friends", tags=["friends"])


def _request_to_out(request: Friendship, requester: User, recipient: User) -> FriendRequestOut:
    return FriendRequestOut(
        id=request.id,
        requester=UserOut.model_validate(requester),
        recipient=UserOut.model_validate(recipient),
        status=request.status,
        created_at=request.created_at,
        responded_at=request.responded_at,
    )


@router.post("/requests", response_model=FriendRequestOut, status_code=201)
def send_friend_request(
    payload: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipient = db.query(User).filter(User.name == payload.recipient_name).first()
    if recipient is None:
        raise HTTPException(status_code=404, detail="No user with that name")
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="You can't send a friend request to yourself")

    existing = friendship_service.get_relationship(db, current_user.id, recipient.id)
    if existing is not None:
        if existing.status == "accepted":
            raise HTTPException(status_code=400, detail="You're already friends")
        if existing.status == "pending":
            raise HTTPException(status_code=400, detail="A request is already pending between you two")
        db.delete(existing)  # previously declined - allow a fresh request
        db.flush()

    request = Friendship(requester_id=current_user.id, recipient_id=recipient.id, status="pending")
    db.add(request)
    db.commit()
    db.refresh(request)
    return _request_to_out(request, current_user, recipient)


@router.get("/requests/incoming", response_model=list[FriendRequestOut])
def incoming_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(Friendship)
        .filter(Friendship.recipient_id == current_user.id, Friendship.status == "pending")
        .all()
    )
    return [_request_to_out(r, db.get(User, r.requester_id), current_user) for r in rows]


@router.get("/requests/outgoing", response_model=list[FriendRequestOut])
def outgoing_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(Friendship)
        .filter(Friendship.requester_id == current_user.id, Friendship.status == "pending")
        .all()
    )
    return [_request_to_out(r, current_user, db.get(User, r.recipient_id)) for r in rows]


@router.post("/requests/{request_id}/accept", response_model=FriendRequestOut)
def accept_request(
    request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    request = db.get(Friendship, request_id)
    if request is None or request.recipient_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found")
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="This request has already been responded to")

    request.status = "accepted"
    request.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(request)
    return _request_to_out(request, db.get(User, request.requester_id), current_user)


@router.post("/requests/{request_id}/decline", response_model=FriendRequestOut)
def decline_request(
    request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    request = db.get(Friendship, request_id)
    if request is None or request.recipient_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found")
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="This request has already been responded to")

    request.status = "declined"
    request.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(request)
    return _request_to_out(request, db.get(User, request.requester_id), current_user)


@router.get("", response_model=list[UserOut])
def list_friends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    friends = friendship_service.list_friends(db, current_user.id)
    return [UserOut.model_validate(f) for f in friends]
