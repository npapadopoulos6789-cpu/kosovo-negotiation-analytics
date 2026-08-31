import pytest
from datetime import date

from app.models.negotiation_event import NegotiationEvent
from app.models.negotiation_analysis import NegotiationAnalysis
from app.schemas.negotiation_analysis import NegotiationAnalysisCreate
from app.services import negotiation_analysis as analysis_service
from app.services.llm_client import LLMCallError
from app.services.negotiation_analysis import (
    NegotiationAnalysisNotFoundError, EventForAnalysisNotFoundError, IdenticalComparisonEventsError
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

    def get_all(self, db):
        return list(self._events.values())


class FakeCountry:
    def __init__(self, id):
        self.id = id


class FakeCountryRepository:
    def get_by_name(self, db, name):
        return FakeCountry(1) if name == "Serbia" else FakeCountry(2)


class FakeIndicatorRepository:
    def get_by_country(self, db, country_id):
        return []


class FakeAnalyticsService:
    """
    Stub του analytics_service -- οι τιμές δεν χρειάζεται να είναι σωστές
    αριθμητικά, μόνο δομικά σωστές (ώστε το context building να τρέξει
    χωρίς σφάλμα). Η ορθότητα του πραγματικού analytics πυρήνα ελέγχεται
    ήδη στο test_analytics_service.py/test_validation_targets.py -- αυτό
    το test file ελέγχει ΜΟΝΟ τη λογική του negotiation_analysis service.
    """
    KEY_YEARS = [1999, 2013, 2023]

    def calculate_power_index(self, db, country_id, year):
        return 50.0

    def calculate_power_gap(self, db, serbia_id, kosovo_id, year):
        return 5.0

    def calculate_window_score(self, db, serbia_id, kosovo_id, year, previous_year):
        return 60.0

    def _most_recent_year_with_data(self, db, serbia_id, kosovo_id, year):
        return None

    def find_optimal_agreement_period(self, db, country_id):
        return {"year": 2013, "power_index": 50.0}

    def find_optimal_mutual_compromise_period(self, db, serbia_id, kosovo_id):
        return {"year": 2013, "window_score": 60.0}

    def find_best_moments(self, db, serbia_id, kosovo_id):
        return []


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


@pytest.fixture()
def fake_context_dependencies(monkeypatch):
    """Μοκάρει ΟΛΑ όσα χρειάζεται το context building (_build_event_context/
    _build_synthesis_context) εκτός event_repository, που έχει ήδη το δικό
    του fixture -- country/indicator repos + ο ίδιος ο analytics_service."""
    monkeypatch.setattr(analysis_service, "country_repository", FakeCountryRepository())
    monkeypatch.setattr(analysis_service, "indicator_repository", FakeIndicatorRepository())
    monkeypatch.setattr(analysis_service, "analytics_service", FakeAnalyticsService())


FAKE_LLM_RAW_TEXT = '{"answer": "fake answer", "answer_certainty": "HIGH", "data_gaps_noted": []}'


@pytest.fixture()
def fake_llm_call(monkeypatch):
    """Μοκάρει το πραγματικό Anthropic call -- ΚΑΝΕΝΑ πραγματικό network
    call δεν πρέπει να γίνεται ποτέ μέσα από pytest. Καταγράφει τα calls
    ώστε τα tests να επιβεβαιώνουν πόσες φορές (και αν) κλήθηκε."""
    calls = []

    def fake_call(system_prompt, user_message, max_tokens=8192):
        calls.append({"system_prompt": system_prompt, "user_message": user_message, "max_tokens": max_tokens})
        return {"raw_text": FAKE_LLM_RAW_TEXT, "model": "fake-model"}

    monkeypatch.setattr(analysis_service.llm_client, "call_llm", fake_call)
    return calls


def test_create_synthesis_analysis_when_no_event_id(
    fake_analysis_repo, fake_event_repo, fake_context_dependencies, fake_llm_call
):
    # negotiation_event_id=None -- πρέπει να γίνει is_synthesis=True αυτόματα
    data = NegotiationAnalysisCreate(user_question="Compare all periods")

    created = analysis_service.create_analysis(db=None, data=data)

    assert created.is_synthesis is True
    assert created.negotiation_event_id is None
    assert created.llm_answer == FAKE_LLM_RAW_TEXT
    assert created.model_used == "fake-model"
    assert len(fake_llm_call) == 1
    # Synthesis ΔΕΝ πειράζεται -- πρέπει να μείνει στο γενικό
    # llm_client.MAX_TOKENS (8192), βλ. σχόλιο πάνω από QA_MAX_TOKENS.
    assert fake_llm_call[0]["max_tokens"] == analysis_service.llm_client.MAX_TOKENS


def test_create_event_specific_analysis(
    fake_analysis_repo, fake_event_repo, fake_context_dependencies, fake_llm_call
):
    fake_event_repo._events[1] = NegotiationEvent(id=1, title="Rambouillet", date=date(1999, 2, 6))
    data = NegotiationAnalysisCreate(negotiation_event_id=1, user_question="Why was ZOPA narrow?")

    created = analysis_service.create_analysis(db=None, data=data)

    assert created.is_synthesis is False
    assert created.negotiation_event_id == 1
    assert created.llm_answer == FAKE_LLM_RAW_TEXT
    assert len(fake_llm_call) == 1
    # Per-event Q&A χρησιμοποιεί το χαμηλότερο QA_MAX_TOKENS -- βασισμένο
    # σε πραγματικό logged output (1540 tokens), βλ. σχόλιο στο service.
    assert fake_llm_call[0]["max_tokens"] == analysis_service.QA_MAX_TOKENS


def test_create_analysis_rejects_missing_event(fake_analysis_repo, fake_event_repo, fake_llm_call):
    data = NegotiationAnalysisCreate(negotiation_event_id=999, user_question="Why?")

    with pytest.raises(EventForAnalysisNotFoundError):
        analysis_service.create_analysis(db=None, data=data)

    # Το event δεν υπάρχει -- δεν πρέπει καν να φτάσουμε στο LLM call
    assert len(fake_llm_call) == 0


def test_create_analysis_does_not_save_when_llm_call_fails(
    fake_analysis_repo, fake_event_repo, fake_context_dependencies, monkeypatch
):
    def failing_call(system_prompt, user_message, max_tokens=8192):
        raise LLMCallError("boom")

    monkeypatch.setattr(analysis_service.llm_client, "call_llm", failing_call)

    data = NegotiationAnalysisCreate(user_question="Compare all periods")

    with pytest.raises(LLMCallError):
        analysis_service.create_analysis(db=None, data=data)

    # Καμία μισή/άκυρη εγγραφή δεν πρέπει να αποθηκευτεί
    assert fake_analysis_repo.get_all(db=None) == []


def test_get_analysis_raises_when_missing(fake_analysis_repo, fake_event_repo):
    with pytest.raises(NegotiationAnalysisNotFoundError):
        analysis_service.get_analysis(db=None, analysis_id=999)


def test_list_analyses_by_event_filters_correctly(
    fake_analysis_repo, fake_event_repo, fake_context_dependencies, fake_llm_call
):
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


def test_create_comparison_happy_path(
    fake_analysis_repo, fake_event_repo, fake_context_dependencies, fake_llm_call
):
    fake_event_repo._events[2] = NegotiationEvent(id=2, title="Rambouillet Talks", date=date(1999, 2, 6))
    fake_event_repo._events[7] = NegotiationEvent(id=7, title="Brussels Agreement", date=date(2013, 4, 19))

    created = analysis_service.create_comparison(db=None, event_a_id=2, event_b_id=7)

    assert created.negotiation_event_id == 2
    assert created.is_synthesis is False
    assert "2" in created.user_question
    assert "7" in created.user_question
    assert created.llm_answer == FAKE_LLM_RAW_TEXT
    # Compare ΔΕΝ πειράζεται -- καμία logged data να δικαιολογήσει
    # χαμηλότερο όριο, μένει στο γενικό llm_client.MAX_TOKENS.
    assert fake_llm_call[0]["max_tokens"] == analysis_service.llm_client.MAX_TOKENS
    assert len(fake_llm_call) == 1
    # Regression: το μήνυμα προς το LLM πρέπει να αναφέρει τους ΠΡΑΓΜΑΤΙΚΟΥΣ
    # τίτλους των events, ΠΟΤΕ "event_a (id=...)"/"event_b (id=...)" -- το
    # μοντέλο τα επανέλαβε αυτολεξεί στην απάντηση όταν το μήνυμα τα είχε
    # (πραγματικό production bug, βλ. _build_compare_message).
    sent_message = fake_llm_call[0]["user_message"]
    assert "Rambouillet Talks" in sent_message
    assert "Brussels Agreement" in sent_message
    assert "event_a (id=" not in sent_message
    assert "event_b (id=" not in sent_message


def test_create_comparison_retranslates_when_response_is_greek(
    fake_analysis_repo, fake_event_repo, fake_context_dependencies, monkeypatch
):
    # Regression: το compare δεν έχει user_question, άρα καμία ελληνική
    # ερώτηση να πυροδοτήσει το _GREEK_CHAR_RE -- το production bug ήταν
    # ότι το μοντέλο απαντούσε ελληνικά έτσι κι αλλιώς (βλ.
    # _translate_json_to_english). Εδώ προσομοιώνουμε ακριβώς αυτό: η
    # ΠΡΩΤΗ κλήση επιστρέφει ελληνικό JSON, η δεύτερη (η μεταφραστική) το
    # αγγλικό ισοδύναμο -- το αποθηκευμένο αποτέλεσμα πρέπει να είναι το
    # δεύτερο, όχι το πρώτο.
    fake_event_repo._events[2] = NegotiationEvent(id=2, title="Rambouillet Talks", date=date(1999, 2, 6))
    fake_event_repo._events[7] = NegotiationEvent(id=7, title="Brussels Agreement", date=date(2013, 4, 19))

    greek_raw_text = (
        '{"zopa_difference": "Η ζώνη ήταν στενότερη", "power_comparison": "...", '
        '"ripeness_difference": "...", "central_contrast": "...", '
        '"answer_certainty": "HIGH", "data_gaps_noted": []}'
    )
    english_raw_text = (
        '{"zopa_difference": "The zone was narrower", "power_comparison": "...", '
        '"ripeness_difference": "...", "central_contrast": "...", '
        '"answer_certainty": "HIGH", "data_gaps_noted": []}'
    )
    calls = []

    def fake_call(system_prompt, user_message, max_tokens=8192):
        calls.append({"system_prompt": system_prompt})
        if len(calls) == 1:
            return {"raw_text": greek_raw_text, "model": "fake-model"}
        return {"raw_text": english_raw_text, "model": "fake-model"}

    monkeypatch.setattr(analysis_service.llm_client, "call_llm", fake_call)

    created = analysis_service.create_comparison(db=None, event_a_id=2, event_b_id=7)

    assert len(calls) == 2
    assert created.llm_answer == english_raw_text
    assert "English" in calls[1]["system_prompt"]


def test_create_comparison_rejects_identical_events(fake_analysis_repo, fake_event_repo, fake_llm_call):
    with pytest.raises(IdenticalComparisonEventsError):
        analysis_service.create_comparison(db=None, event_a_id=2, event_b_id=2)

    # Ίδια πλευρά -- δεν πρέπει καν να φτάσουμε στο event lookup/LLM call
    assert len(fake_llm_call) == 0


def test_create_comparison_rejects_missing_event(fake_analysis_repo, fake_event_repo, fake_llm_call):
    fake_event_repo._events[2] = NegotiationEvent(id=2, title="Rambouillet Talks", date=date(1999, 2, 6))

    with pytest.raises(EventForAnalysisNotFoundError):
        analysis_service.create_comparison(db=None, event_a_id=2, event_b_id=999)

    assert len(fake_llm_call) == 0
