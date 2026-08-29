from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.models.user import User
from app.services import negotiation_analysis as analysis_service
from app.schemas.negotiation_analysis import CompareCreate, NegotiationAnalysisRead

router = APIRouter(tags=["Compare"])


@router.post("/compare", response_model=NegotiationAnalysisRead, status_code=201)
@limiter.limit("5/hour")
def create_comparison(
    request: Request,
    payload: CompareCreate,
    db: Session = Depends(get_db),
    # Οποιοσδήποτε συνδεδεμένος χρήστης -- ίδιος κανόνας/σχόλιο με το
    # synthesis.py router, βλ. εκεί.
    current_user: User = Depends(get_current_user),
):
    # Καμία business logic εδώ -- μόνο DI + κλήση στο service, ίδιο μοτίβο
    # με το synthesis.py router.
    return analysis_service.create_comparison(db, payload.event_a_id, payload.event_b_id)
