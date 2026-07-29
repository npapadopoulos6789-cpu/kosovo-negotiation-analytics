from sqlalchemy.orm import Session, joinedload

from app.models.negotiation_event import NegotiationEvent, EventParticipant


def get_all(db: Session) -> list[NegotiationEvent]:
    # joinedload(...participants) -- λέει στο SQLAlchemy "όταν φέρνεις τα
    # events, φέρε ΜΑΖΙ και τους participants τους σε ΕΝΑ query", αντί να
    # κάνει ένα ξεχωριστό query για τους participants κάθε event (πιο αργό)
    return (
        db.query(NegotiationEvent)
        .options(joinedload(NegotiationEvent.participants).joinedload(EventParticipant.country))
        .order_by(NegotiationEvent.date)
        .all()
    )


def get_by_id(db: Session, event_id: int) -> NegotiationEvent | None:
    return (
        db.query(NegotiationEvent)
        .options(joinedload(NegotiationEvent.participants).joinedload(EventParticipant.country))
        .filter(NegotiationEvent.id == event_id)
        .first()
    )


def create(db: Session, event: NegotiationEvent) -> NegotiationEvent:
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update(db: Session, event: NegotiationEvent, data: dict) -> NegotiationEvent:
    for field, value in data.items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


def delete(db: Session, event: NegotiationEvent) -> None:
    db.delete(event)
    db.commit()


def replace_participants(
    db: Session, event: NegotiationEvent, participants_data: list[dict]
) -> None:
    # Σβήνουμε όλους τους υπάρχοντες participants του event...
    for p in list(event.participants):
        db.delete(p)
    db.flush()  # "στέλνει" τις διαγραφές στη ΒΔ χωρίς ακόμα commit

    # ...και δημιουργούμε νέους, βάσει της λίστας που δόθηκε
    for p_data in participants_data:
        participant = EventParticipant(event_id=event.id, **p_data)
        db.add(participant)

    db.commit()
    db.refresh(event)