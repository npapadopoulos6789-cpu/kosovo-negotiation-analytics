from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.models.user import User
from app.services import negotiation_analysis as analysis_service
from app.schemas.negotiation_analysis import (
    NegotiationAnalysisCreate, NegotiationAnalysisRead, SynthesisCreate
)

router = APIRouter(tags=["Synthesis"])


@router.post("/synthesis", response_model=NegotiationAnalysisRead, status_code=201)
@limiter.limit("5/hour")
def create_synthesis(
    request: Request,
    payload: SynthesisCreate,
    db: Session = Depends(get_db),
    # Οποιοσδήποτε συνδεδεμένος χρήστης (VIEWER ή ADMIN) -- ΟΧΙ
    # require_admin. Δίνει νόημα στο "δωρεάν λογαριασμό" (βλ.
    # RegisterPage), δεν είναι admin-only λειτουργία. 401 αν λείπει/είναι
    # άκυρο το token, αυτόματα από το get_current_user.
    current_user: User = Depends(get_current_user),
):
    # negotiation_event_id=None -> το ίδιο create_analysis το αναγνωρίζει
    # ως synthesis (is_synthesis=True) και χτίζει το synthesis context,
    # χωρίς καμία διπλή λογική εδώ.
    data = NegotiationAnalysisCreate(negotiation_event_id=None, user_question=payload.user_question)
    return analysis_service.create_analysis(db, data)
