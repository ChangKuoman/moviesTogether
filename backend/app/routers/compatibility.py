from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import UserOut
from app.schemas.compatibility import (
    CompatibilityMatrixOut,
    CompatibilityOut,
    CompatibilityPairOut,
    WatchTogetherItemOut,
)
from app.services import compatibility_service, friendship_service, model_service

router = APIRouter(prefix="/api/compatibility", tags=["compatibility"])


def _factors_or_422(db: Session) -> dict:
    factors = model_service.load_latest_factors(db)
    if factors is None:
        raise HTTPException(
            status_code=422, detail="Not enough ratings yet — rate a few more items first."
        )
    return factors


def _validate_pair(db: Session, current_user: User, user_a: int, user_b: int) -> tuple[User, User]:
    if user_a == user_b:
        raise HTTPException(status_code=400, detail="user_a and user_b must be different users")
    if current_user.id not in (user_a, user_b):
        raise HTTPException(status_code=403, detail="You can only view compatibility that includes you")

    ua, ub = db.get(User, user_a), db.get(User, user_b)
    if ua is None or ub is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not friendship_service.are_friends(db, user_a, user_b):
        raise HTTPException(status_code=403, detail="You can only compare compatibility with friends")
    return ua, ub


@router.get("", response_model=CompatibilityOut)
def compatibility(
    user_a: int,
    user_b: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ua, ub = _validate_pair(db, current_user, user_a, user_b)
    factors = _factors_or_422(db)
    try:
        result = compatibility_service.compute_compatibility(db, factors, user_a, user_b)
    except compatibility_service.UsersNotComparableError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return CompatibilityOut(user_a=UserOut.model_validate(ua), user_b=UserOut.model_validate(ub), **result)


@router.get("/matrix", response_model=CompatibilityMatrixOut)
def compatibility_matrix(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Compatibility between the current user and each of their accepted friends."""
    factors = _factors_or_422(db)
    friends = friendship_service.list_friends(db, current_user.id)

    pairs = []
    for friend in friends:
        try:
            result = compatibility_service.compute_compatibility(db, factors, current_user.id, friend.id)
        except compatibility_service.UsersNotComparableError:
            continue
        pairs.append(
            CompatibilityPairOut(
                user_a_id=current_user.id,
                user_b_id=friend.id,
                score_pct=result["score_pct"],
                overlap_count=result["overlap_count"],
            )
        )

    return CompatibilityMatrixOut(
        users=[UserOut.model_validate(current_user)] + [UserOut.model_validate(f) for f in friends],
        pairs=pairs,
    )


@router.get("/watch-together", response_model=list[WatchTogetherItemOut])
def watch_together(
    user_a: int,
    user_b: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Candidates from either of your libraries that you haven't BOTH rated, ranked by how good
    a joint pick they'd be. Each item is flagged with rated_by_a/rated_by_b so the caller can
    split into 'neither watched' / 'you watched' / 'friend watched' sections."""
    _validate_pair(db, current_user, user_a, user_b)
    factors = _factors_or_422(db)
    results = compatibility_service.compute_watch_together(db, factors, user_a, user_b)
    return [WatchTogetherItemOut(**r) for r in results]
