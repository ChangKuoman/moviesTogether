from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.analysis import HybridOut
from app.services import hybrid_service, model_service

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/hybrid", response_model=HybridOut)
def hybrid(
    w_collab: float = 0.6,
    w_content: float = 0.4,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    factors = model_service.load_latest_factors(db)
    if factors is None:
        raise HTTPException(
            status_code=422, detail="Not enough ratings yet — rate a few more items first."
        )

    items = hybrid_service.compute_hybrid_recommendations(
        db, factors, current_user.id, w_collab, w_content
    )
    return HybridOut(w_collab=w_collab, w_content=w_content, items=items)
