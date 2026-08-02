from sqlalchemy.orm import Session

from app.models.negotiation_analysis import NegotiationAnalysis


def get_all(db: Session) -> list[NegotiationAnalysis]:
    return db.query(NegotiationAnalysis).order_by(NegotiationAnalysis.id).all()


def get_by_id(db: Session, analysis_id: int) -> NegotiationAnalysis | None:
    return db.query(NegotiationAnalysis).filter(NegotiationAnalysis.id == analysis_id).first()


def get_by_event(db: Session, event_id: int) -> list[NegotiationAnalysis]:
    return db.query(NegotiationAnalysis).filter(
        NegotiationAnalysis.negotiation_event_id == event_id
    ).all()


def create(db: Session, analysis: NegotiationAnalysis) -> NegotiationAnalysis:
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis