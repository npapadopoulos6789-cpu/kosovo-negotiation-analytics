from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import negotiation_analysis as analysis_service
from app.schemas.negotiation_analysis import (
    NegotiationAnalysisCreate, NegotiationAnalysisRead, SynthesisCreate
)

router = APIRouter(tags=["Synthesis"])


@router.post("/synthesis", response_model=NegotiationAnalysisRead, status_code=201)
def create_synthesis(payload: SynthesisCreate, db: Session = Depends(get_db)):
    # negotiation_event_id=None -> το ίδιο create_analysis το αναγνωρίζει
    # ως synthesis (is_synthesis=True) και χτίζει το synthesis context,
    # χωρίς καμία διπλή λογική εδώ.
    data = NegotiationAnalysisCreate(negotiation_event_id=None, user_question=payload.user_question)
    return analysis_service.create_analysis(db, data)
