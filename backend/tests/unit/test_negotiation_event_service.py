import pytest
from datetime import date

from app.models.country import Country
from app.models.negotiation_event import NegotiationEvent, EventParticipant
from app.schemas.negotiation_event import (
    NegotiationEventCreate, NegotiationEventUpdate, ParticipantCreate
)
from app.services import negotiation_event as event_service
from app.services.negotiation_event import (
    NegotiationEventNotFoundError, InvalidWeightsError, CountryForParticipantNotFoundError,
    EventHasAnalysesError
)


class FakeEventRepository:
    def __init__(self):
        self._events: dict[int, NegotiationEvent] = {}
        self._next_id = 1

    def get_all(self, db):
        return list(self._events.values())

    def get_by_id(self, db, event_id):
        return self._events.get(event_id)

    def create(self, db, event):
        event.id = self._next_id
        self._next_id += 1
        event.participants = []
        self._events[event.id] = event
        return event

    def update(self, db, event, data):
        for field, value in data.items():
            setattr(event, field, value)
        return event

    def delete(self, db, event):
        del self._events[event.id]

    def replace_participants(self, db, event, participants_data):
        event.participants = [
            EventParticipant(country_id=p["country_id"], role=p["role"])
            for p in participants_data
        ]


class FakeCountryRepository:
    def __init__(self):
        self._countries: dict[int, Country] = {}

    def get_by_id(self, db, country_id):
        return self._countries.get(country_id)


@pytest.fixture()
def fake_event_repo(monkeypatch):
    repo = FakeEventRepository()
    monkeypatch.setattr(event_service, "event_repository", repo)
    return repo


@pytest.fixture()
def fake_country_repo(monkeypatch):
    repo = FakeCountryRepository()
    monkeypatch.setattr(event_service, "country_repository", repo)
    return repo


class FakeAnalysisRepository:
    def __init__(self):
        # event_id -> πόσα analyses "υπάρχουν" γι' αυτό -- ο ίδιος fake
        # μπορεί να ρυθμιστεί από κάθε test (βλ. test_delete_event_rejects...)
        self._by_event: dict[int, list[object]] = {}

    def get_by_event(self, db, event_id):
        return self._by_event.get(event_id, [])


@pytest.fixture()
def fake_analysis_repo(monkeypatch):
    repo = FakeAnalysisRepository()
    monkeypatch.setattr(event_service, "analysis_repository", repo)
    return repo


def make_event_data(**overrides):
    defaults = dict(
        title="Rambouillet Talks",
        date=date(1999, 2, 6),
        economic_weight=4,
        military_weight=4,
        social_weight=2,
        participants=[],
    )
    defaults.update(overrides)
    return NegotiationEventCreate(**defaults)


def test_create_event_with_valid_weights(fake_event_repo, fake_country_repo):
    data = make_event_data()

    created = event_service.create_event(db=None, data=data)

    assert created.id is not None
    assert created.title == "Rambouillet Talks"


def test_create_event_rejects_invalid_weights(fake_event_repo, fake_country_repo):
    data = make_event_data(economic_weight=5, military_weight=5, social_weight=5)

    with pytest.raises(InvalidWeightsError):
        event_service.create_event(db=None, data=data)


def test_create_event_rejects_missing_participant_country(fake_event_repo, fake_country_repo):
    data = make_event_data(participants=[ParticipantCreate(country_id=1, role="PARTY")])

    with pytest.raises(CountryForParticipantNotFoundError):
        event_service.create_event(db=None, data=data)


def test_create_event_with_valid_participants(fake_event_repo, fake_country_repo):
    fake_country_repo._countries[1] = Country(id=1, name="Serbia")
    data = make_event_data(participants=[ParticipantCreate(country_id=1, role="PARTY")])

    created = event_service.create_event(db=None, data=data)

    assert len(created.participants) == 1
    assert created.participants[0].country_id == 1


def test_get_event_raises_when_missing(fake_event_repo, fake_country_repo):
    with pytest.raises(NegotiationEventNotFoundError):
        event_service.get_event(db=None, event_id=999)


def test_update_event_rejects_broken_weights_from_partial_update(fake_event_repo, fake_country_repo):
    created = event_service.create_event(db=None, data=make_event_data())

    # Στέλνουμε update ΜΟΝΟ για economic_weight -- αυτό ΘΑ ΕΠΡΕΠΕ να σπάσει
    # το άθροισμα (6 + 4 + 2 = 12), ακριβώς το σενάριο που θέλαμε να πιάσουμε
    with pytest.raises(InvalidWeightsError):
        event_service.update_event(
            db=None, event_id=created.id,
            data=NegotiationEventUpdate(economic_weight=6)
        )


def test_update_event_allows_valid_partial_update(fake_event_repo, fake_country_repo):
    created = event_service.create_event(db=None, data=make_event_data())

    updated = event_service.update_event(
        db=None, event_id=created.id,
        data=NegotiationEventUpdate(title="Renamed Event")
    )

    assert updated.title == "Renamed Event"
    # Τα βάρη έμειναν ίδια, δεν άλλαξαν
    assert updated.economic_weight == 4


def test_delete_event_removes_entry(fake_event_repo, fake_country_repo, fake_analysis_repo):
    created = event_service.create_event(db=None, data=make_event_data())

    event_service.delete_event(db=None, event_id=created.id)

    assert fake_event_repo.get_by_id(None, created.id) is None


def test_delete_event_rejects_when_analyses_exist(fake_event_repo, fake_country_repo, fake_analysis_repo):
    # Χωρίς αυτόν τον έλεγχο, το delete θα προσπαθούσε να σβήσει το event
    # και θα έσκαγε σε ακατέργαστο Postgres IntegrityError (FK χωρίς
    # ondelete) -- βλ. σχόλιο στο EventHasAnalysesError. Το service ΠΡΕΠΕΙ
    # να το πιάσει ΠΡΙΝ φτάσει καν στο repository.delete.
    created = event_service.create_event(db=None, data=make_event_data())
    fake_analysis_repo._by_event[created.id] = ["fake analysis 1", "fake analysis 2"]

    with pytest.raises(EventHasAnalysesError):
        event_service.delete_event(db=None, event_id=created.id)

    # Το event ΔΕΝ διαγράφηκε -- το block είναι πραγματικό, όχι απλά raise
    # μετά το γεγονός
    assert fake_event_repo.get_by_id(None, created.id) is not None