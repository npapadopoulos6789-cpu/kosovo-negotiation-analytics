from sqlalchemy.orm import Session

from app.models.negotiation_analysis import NegotiationAnalysis
from app.repositories import negotiation_analysis as analysis_repository
from app.repositories import negotiation_event as event_repository
from app.schemas.negotiation_analysis import NegotiationAnalysisCreate


class NegotiationAnalysisNotFoundError(Exception):
    def __init__(self, analysis_id: int):
        self.analysis_id = analysis_id
        super().__init__(f"NegotiationAnalysis {analysis_id} not found")


class EventForAnalysisNotFoundError(Exception):
    def __init__(self, event_id: int):
        self.event_id = event_id
        super().__init__(f"NegotiationEvent {event_id} not found for analysis")


def list_analyses(db: Session) -> list[NegotiationAnalysis]:
    return analysis_repository.get_all(db)


def get_analysis(db: Session, analysis_id: int) -> NegotiationAnalysis:
    analysis = analysis_repository.get_by_id(db, analysis_id)
    if analysis is None:
        raise NegotiationAnalysisNotFoundError(analysis_id)
    return analysis


def list_analyses_by_event(db: Session, event_id: int) -> list[NegotiationAnalysis]:
    return analysis_repository.get_by_event(db, event_id)


def create_analysis(db: Session, data: NegotiationAnalysisCreate) -> NegotiationAnalysis:
    is_synthesis = data.negotiation_event_id is None

    # Business rule: αν ΔΕΝ είναι synthesis (δηλαδή αναφέρεται σε
    # συγκεκριμένο event), το event αυτό πρέπει να υπάρχει πραγματικά
    if not is_synthesis:
        if event_repository.get_by_id(db, data.negotiation_event_id) is None:
            raise EventForAnalysisNotFoundError(data.negotiation_event_id)

    # ΠΡΟΣΩΡΙΝΑ: δεν καλούμε ακόμα το LLM -- απλά αποθηκεύουμε την
    # ερώτηση, με άδεια απάντηση. Το πραγματικό LLM integration
    # (system prompt, OpenAI API call) είναι το ΕΠΟΜΕΝΟ, ξεχωριστό βήμα.
    analysis = NegotiationAnalysis(
        negotiation_event_id=data.negotiation_event_id,
        is_synthesis=is_synthesis,
        user_question=data.user_question,
        llm_answer=None,
        model_used=None,
    )
    return analysis_repository.create(db, analysis)