from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.services import negotiation_analysis as analysis_service
from app.schemas.negotiation_analysis import CompareCreate, NegotiationAnalysisRead

router = APIRouter(tags=["Compare"])


@router.post("/compare", response_model=NegotiationAnalysisRead, status_code=201)
@limiter.limit("5/hour")
def create_comparison(request: Request, payload: CompareCreate, db: Session = Depends(get_db)):
    # Καμία business logic εδώ -- μόνο DI + κλήση στο service, ίδιο μοτίβο
    # με το synthesis.py router.
    return analysis_service.create_comparison(db, payload.event_a_id, payload.event_b_id)
