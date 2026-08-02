from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import negotiation_analysis as analysis_service
from app.schemas.negotiation_analysis import NegotiationAnalysisCreate, NegotiationAnalysisRead

router = APIRouter(prefix="/negotiation-analyses", tags=["Negotiation Analyses"])


@router.get("/", response_model=list[NegotiationAnalysisRead])
def list_analyses(db: Session = Depends(get_db)):
    return analysis_service.list_analyses(db)


@router.get("/{analysis_id}", response_model=NegotiationAnalysisRead)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    return analysis_service.get_analysis(db, analysis_id)


@router.get("/by-event/{event_id}", response_model=list[NegotiationAnalysisRead])
def list_analyses_by_event(event_id: int, db: Session = Depends(get_db)):
    return analysis_service.list_analyses_by_event(db, event_id)


@router.post("/", response_model=NegotiationAnalysisRead, status_code=201)
def create_analysis(payload: NegotiationAnalysisCreate, db: Session = Depends(get_db)):
    # ΣΗΜΕΙΩΣΗ: δεν βάζουμε require_admin εδώ -- θυμήσου το domain model
    # μας, ΟΠΟΙΟΣΔΗΠΟΤΕ συνδεδεμένος χρήστης (ADMIN ή VIEWER) επιτρέπεται
    # να ζητήσει LLM analysis, μόνο η διαχείριση δεδομένων (Country/
    # Indicator/Event) είναι ADMIN-only
    return analysis_service.create_analysis(db, payload)
