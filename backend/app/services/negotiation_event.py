from sqlalchemy.orm import Session

from app.models.negotiation_event import NegotiationEvent
from app.repositories import negotiation_event as event_repository
from app.repositories import country as country_repository
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


def _validate_weights(economic: int, military: int, social: int) -> None:
    if economic + military + social != 10:
        raise InvalidWeightsError(economic, military, social)


def _validate_participant_countries(db: Session, participants_data: list) -> None:
    for p in participants_data:
        country_id = p["country_id"] if isinstance(p, dict) else p.country_id
        if country_repository.get_by_id(db, country_id) is None:
            raise CountryForParticipantNotFoundError(country_id)


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
    event_repository.delete(db, event)