from sqlalchemy.orm import Session

from app.models.negotiation_event import NegotiationEvent
from app.repositories import negotiation_event as event_repository
from app.repositories import country as country_repository
from app.repositories import negotiation_analysis as analysis_repository
from app.schemas.negotiation_event import NegotiationEventCreate, NegotiationEventUpdate


class NegotiationEventNotFoundError(Exception):
    def __init__(self, event_id: int):
        self.event_id = event_id
        super().__init__(f"NegotiationEvent {event_id} not found")


class InvalidWeightsError(Exception):
    # Το πιο σημαντικό μας business rule -- τα βάρη πρέπει να αθροίζουν σε 10
    def __init__(self, economic: int, military: int, social: int):
        total = economic + military + social
        super().__init__(
            f"Weights must sum to 10, got {total} "
            f"(economic={economic}, military={military}, social={social})"
        )


class CountryForParticipantNotFoundError(Exception):
    def __init__(self, country_id: int):
        self.country_id = country_id
        super().__init__(f"Country {country_id} not found for participant")


class EventHasAnalysesError(Exception):
    # Το FK NegotiationAnalysis.negotiation_event_id δεν έχει ondelete
    # clause -- χωρίς αυτόν τον έλεγχο, ένα DELETE πάνω σε event με
    # analyses θα έσκαγε με ακατέργαστο Postgres IntegrityError αντί για
    # καθαρό 409. Block αντί για cascade/SET NULL: τα LLM Q&A analyses
    # είναι ερευνητικό output, δεν σβήνονται σιωπηλά.
    def __init__(self, event_id: int, analysis_count: int):
        self.event_id = event_id
        self.analysis_count = analysis_count
        super().__init__(
            f"Cannot delete event {event_id}: {analysis_count} analysis/analyses "
            f"still reference it. Delete those analyses first."
        )


def _validate_weights(economic: int, military: int, social: int) -> None:
    if economic + military + social != 10:
        raise InvalidWeightsError(economic, military, social)


def _validate_participant_countries(db: Session, participants_data: list) -> None:
    for p in participants_data:
        if isinstance(p, dict):
            country_id = p["country_id"]
            supports_country_id = p.get("supports_country_id")
        else:
            country_id = p.country_id
            supports_country_id = p.supports_country_id
        if country_repository.get_by_id(db, country_id) is None:
            raise CountryForParticipantNotFoundError(country_id)
        if supports_country_id is not None and country_repository.get_by_id(db, supports_country_id) is None:
            raise CountryForParticipantNotFoundError(supports_country_id)


def list_events(db: Session) -> list[NegotiationEvent]:
    return event_repository.get_all(db)


def get_event(db: Session, event_id: int) -> NegotiationEvent:
    event = event_repository.get_by_id(db, event_id)
    if event is None:
        raise NegotiationEventNotFoundError(event_id)
    return event


def create_event(db: Session, data: NegotiationEventCreate) -> NegotiationEvent:
    _validate_weights(data.economic_weight, data.military_weight, data.social_weight)
    _validate_participant_countries(db, data.participants)

    event_data = data.model_dump(exclude={"participants"})
    event = NegotiationEvent(**event_data)
    event = event_repository.create(db, event)

    if data.participants:
        participants_data = [p.model_dump() for p in data.participants]
        event_repository.replace_participants(db, event, participants_data)

    return event


def update_event(db: Session, event_id: int, data: NegotiationEventUpdate) -> NegotiationEvent:
    event = get_event(db, event_id)

    update_data = data.model_dump(exclude_unset=True, exclude={"participants"})

    # ΣΗΜΑΝΤΙΚΟ: υπολογίζουμε το ΤΕΛΙΚΟ άθροισμα μετά την αλλαγή, όχι μόνο
    # τα πεδία που στάλθηκαν -- έτσι πιάνουμε το σενάριο "άλλαξα μόνο το
    # economic_weight και έσπασα το άθροισμα των άλλων δύο"
    final_economic = update_data.get("economic_weight", event.economic_weight)
    final_military = update_data.get("military_weight", event.military_weight)
    final_social = update_data.get("social_weight", event.social_weight)
    _validate_weights(final_economic, final_military, final_social)

    if data.participants is not None:
        _validate_participant_countries(db, data.participants)

    event = event_repository.update(db, event, update_data)

    if data.participants is not None:
        participants_data = [p.model_dump() for p in data.participants]
        event_repository.replace_participants(db, event, participants_data)

    return event


def delete_event(db: Session, event_id: int) -> None:
    event = get_event(db, event_id)
    existing_analyses = analysis_repository.get_by_event(db, event_id)
    if existing_analyses:
        raise EventHasAnalysesError(event_id, len(existing_analyses))
    event_repository.delete(db, event)