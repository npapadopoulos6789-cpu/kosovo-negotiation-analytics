import pytest
from datetime import date

from app.models.negotiation_event import NegotiationEvent
from app.models.negotiation_analysis import NegotiationAnalysis
from app.schemas.negotiation_analysis import NegotiationAnalysisCreate
from app.services import negotiation_analysis as analysis_service
from app.services.negotiation_analysis import (
    NegotiationAnalysisNotFoundError, EventForAnalysisNotFoundError
)


class FakeAnalysisRepository:
    def __init__(self):
        self._analyses: dict[int, NegotiationAnalysis] = {}
        self._next_id = 1

    def get_all(self, db):
        return list(self._analyses.values())

    def get_by_id(self, db, analysis_id):
        return self._analyses.get(analysis_id)

    def get_by_event(self, db, event_id):
        return [a for a in self._analyses.values() if a.negotiation_event_id == event_id]

    def create(self, db, analysis):
        analysis.id = self._next_id
        self._next_id += 1
        self._analyses[analysis.id] = analysis
        return analysis


class FakeEventRepository:
    def __init__(self):
        self._events: dict[int, NegotiationEvent] = {}

    def get_by_id(self, db, event_id):
        return self._events.get(event_id)


@pytest.fixture()
def fake_analysis_repo(monkeypatch):
    repo = FakeAnalysisRepository()
    monkeypatch.setattr(analysis_service, "analysis_repository", repo)
    return repo


@pytest.fixture()
def fake_event_repo(monkeypatch):
    repo = FakeEventRepository()
    monkeypatch.setattr(analysis_service, "event_repository", repo)
    return repo


def test_create_synthesis_analysis_when_no_event_id(fake_analysis_repo, fake_event_repo):
    # negotiation_event_id=None -- πρέπει να γίνει is_synthesis=True αυτόματα
    data = NegotiationAnalysisCreate(user_question="Compare all periods")

    created = analysis_service.create_analysis(db=None, data=data)

    assert created.is_synthesis is True
    assert created.negotiation_event_id is None
    assert created.llm_answer is None  # δεν έχει απαντηθεί ακόμα


def test_create_event_specific_analysis(fake_analysis_repo, fake_event_repo):
    fake_event_repo._events[1] = NegotiationEvent(id=1, title="Rambouillet", date=date(1999, 2, 6))
    data = NegotiationAnalysisCreate(negotiation_event_id=1, user_question="Why was ZOPA narrow?")

    created = analysis_service.create_analysis(db=None, data=data)

    assert created.is_synthesis is False
    assert created.negotiation_event_id == 1


def test_create_analysis_rejects_missing_event(fake_analysis_repo, fake_event_repo):
    data = NegotiationAnalysisCreate(negotiation_event_id=999, user_question="Why?")

    with pytest.raises(EventForAnalysisNotFoundError):
        analysis_service.create_analysis(db=None, data=data)


def test_get_analysis_raises_when_missing(fake_analysis_repo, fake_event_repo):
    with pytest.raises(NegotiationAnalysisNotFoundError):
        analysis_service.get_analysis(db=None, analysis_id=999)


def test_list_analyses_by_event_filters_correctly(fake_analysis_repo, fake_event_repo):
    fake_event_repo._events[1] = NegotiationEvent(id=1, title="Event A", date=date(2000, 1, 1))
    fake_event_repo._events[2] = NegotiationEvent(id=2, title="Event B", date=date(2001, 1, 1))

    analysis_service.create_analysis(
        db=None, data=NegotiationAnalysisCreate(negotiation_event_id=1, user_question="Q1")
    )
    analysis_service.create_analysis(
        db=None, data=NegotiationAnalysisCreate(negotiation_event_id=2, user_question="Q2")
    )

    result = analysis_service.list_analyses_by_event(db=None, event_id=1)

    assert len(result) == 1
    assert result[0].negotiation_event_id == 1