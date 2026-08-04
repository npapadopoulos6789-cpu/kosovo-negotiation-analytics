import json

from sqlalchemy.orm import Session

from app.models.negotiation_analysis import NegotiationAnalysis
from app.models.negotiation_event import NegotiationEvent
from app.repositories import negotiation_analysis as analysis_repository
from app.repositories import negotiation_event as event_repository
from app.repositories import indicator as indicator_repository
from app.repositories import country as country_repository
from app.schemas.negotiation_analysis import NegotiationAnalysisCreate
from app.services import analytics as analytics_service
from app.services import llm_client
from app.services.llm_prompts import SYSTEM_PROMPT_QA, SYSTEM_PROMPT_SYNTHESIS, SYSTEM_PROMPT_COMPARE


class NegotiationAnalysisNotFoundError(Exception):
    def __init__(self, analysis_id: int):
        self.analysis_id = analysis_id
        super().__init__(f"NegotiationAnalysis {analysis_id} not found")


class EventForAnalysisNotFoundError(Exception):
    def __init__(self, event_id: int):
        self.event_id = event_id
        super().__init__(f"NegotiationEvent {event_id} not found for analysis")


class IdenticalComparisonEventsError(Exception):
    def __init__(self, event_id: int):
        self.event_id = event_id
        super().__init__(f"Cannot compare NegotiationEvent {event_id} with itself")


def list_analyses(db: Session) -> list[NegotiationAnalysis]:
    return analysis_repository.get_all(db)


def get_analysis(db: Session, analysis_id: int) -> NegotiationAnalysis:
    analysis = analysis_repository.get_by_id(db, analysis_id)
    if analysis is None:
        raise NegotiationAnalysisNotFoundError(analysis_id)
    return analysis


def list_analyses_by_event(db: Session, event_id: int) -> list[NegotiationAnalysis]:
    return analysis_repository.get_by_event(db, event_id)


# ---------------------------------------------------------------------------
# Context building -- ΜΟΝΟ δομημένα δεδομένα, καμία LLM κλήση εδώ
# ---------------------------------------------------------------------------

def _serialize_event(event: NegotiationEvent) -> dict:
    return {
        "id": event.id,
        "title": event.title,
        "date": event.date.isoformat(),
        "description": event.description,
        "zopa_size": event.zopa_size.value if event.zopa_size else None,
        "zopa_reasoning": event.zopa_reasoning,
        "ripeness_status": event.ripeness_status.value if event.ripeness_status else None,
        "ripeness_reasoning": event.ripeness_reasoning,
        "batna_side_a": event.batna_side_a,
        "batna_side_b": event.batna_side_b,
        "red_lines_side_a": event.red_lines_side_a,
        "red_lines_side_b": event.red_lines_side_b,
        "negotiation_type": event.negotiation_type.value if event.negotiation_type else None,
        "economic_weight": event.economic_weight,
        "military_weight": event.military_weight,
        "social_weight": event.social_weight,
        "implementation_success": event.implementation_success,
        "participants": [
            {"country_name": p.country_name, "role": p.role.value}
            for p in event.participants
        ],
    }


def _serialize_indicators_by_category(indicators: list) -> dict:
    grouped: dict[str, list] = {}
    for ind in indicators:
        grouped.setdefault(ind.category.value, []).append({
            "indicator_type": ind.indicator_type,
            "year": ind.year,
            "value": ind.value,
            "unit": ind.unit,
            "source": ind.source,
            "is_verified": ind.is_verified,
            "confidence": ind.confidence.value if ind.confidence else None,
        })
    return grouped


def _window_score_for_year(db: Session, serbia_id: int, kosovo_id: int, year: int) -> float | None:
    # Ίδιο auto-compute previous_year pattern με το /analytics/window-score/{year}
    # (Finding A fix) -- ώστε το context να συμφωνεί με τα analytics endpoints.
    previous_year = None
    if year in analytics_service.KEY_YEARS:
        previous_year = analytics_service._most_recent_year_with_data(
            db, serbia_id, kosovo_id, year
        )
    return analytics_service.calculate_window_score(db, serbia_id, kosovo_id, year, previous_year)


def _build_event_context(db: Session, event: NegotiationEvent) -> dict:
    serbia = country_repository.get_by_name(db, "Serbia")
    kosovo = country_repository.get_by_name(db, "Kosovo")

    year = event.date.year
    year_window = range(year - 2, year + 3)

    serbia_indicators = [
        ind for ind in indicator_repository.get_by_country(db, serbia.id)
        if ind.year in year_window
    ]
    kosovo_indicators = [
        ind for ind in indicator_repository.get_by_country(db, kosovo.id)
        if ind.year in year_window
    ]

    return {
        "event": _serialize_event(event),
        "indicators": {
            "Serbia": _serialize_indicators_by_category(serbia_indicators),
            "Kosovo": _serialize_indicators_by_category(kosovo_indicators),
        },
        "analytics": {
            "year": year,
            "power_index_serbia": analytics_service.calculate_power_index(db, serbia.id, year),
            "power_index_kosovo": analytics_service.calculate_power_index(db, kosovo.id, year),
            "power_gap": analytics_service.calculate_power_gap(db, serbia.id, kosovo.id, year),
            "window_score": _window_score_for_year(db, serbia.id, kosovo.id, year),
            "optimal_agreement_period_serbia": analytics_service.find_optimal_agreement_period(db, serbia.id),
            "optimal_agreement_period_kosovo": analytics_service.find_optimal_agreement_period(db, kosovo.id),
            "optimal_mutual_compromise_period": analytics_service.find_optimal_mutual_compromise_period(
                db, serbia.id, kosovo.id
            ),
        },
    }


def _build_synthesis_context(db: Session) -> dict:
    serbia = country_repository.get_by_name(db, "Serbia")
    kosovo = country_repository.get_by_name(db, "Kosovo")

    events = event_repository.get_all(db)

    timeline = [
        {
            "year": year,
            "power_index_serbia": analytics_service.calculate_power_index(db, serbia.id, year),
            "power_index_kosovo": analytics_service.calculate_power_index(db, kosovo.id, year),
            "power_gap": analytics_service.calculate_power_gap(db, serbia.id, kosovo.id, year),
            "window_score": _window_score_for_year(db, serbia.id, kosovo.id, year),
        }
        for year in analytics_service.KEY_YEARS
    ]

    return {
        "events": [_serialize_event(e) for e in events],
        "timeline": timeline,
        "optimal_agreement_period_serbia": analytics_service.find_optimal_agreement_period(db, serbia.id),
        "optimal_agreement_period_kosovo": analytics_service.find_optimal_agreement_period(db, kosovo.id),
        "optimal_mutual_compromise_period": analytics_service.find_optimal_mutual_compromise_period(
            db, serbia.id, kosovo.id
        ),
        "best_moments": analytics_service.find_best_moments(db, serbia.id, kosovo.id),
    }


def _build_compare_context(db: Session, event_a: NegotiationEvent, event_b: NegotiationEvent) -> dict:
    # reuse _build_event_context ×2 -- ίδια δομημένα πεδία + indicators +
    # analytics ανά event, χωρίς διπλή λογική εδώ
    return {
        "event_a": _build_event_context(db, event_a),
        "event_b": _build_event_context(db, event_b),
    }


def _build_user_message(user_question: str, context: dict) -> str:
    return (
        f"ΕΡΩΤΗΣΗ ΧΡΗΣΤΗ: {user_question}\n\n"
        f"CONTEXT (JSON):\n{json.dumps(context, ensure_ascii=False, indent=2)}"
    )


def _build_compare_message(context: dict) -> str:
    # Δεν υπάρχει free-text ερώτηση χρήστη στο compare -- μόνο τα δύο events
    return (
        f"ΣΥΓΚΡΙΣΗ EVENTS: event_a (id={context['event_a']['event']['id']}) vs "
        f"event_b (id={context['event_b']['event']['id']})\n\n"
        f"CONTEXT (JSON):\n{json.dumps(context, ensure_ascii=False, indent=2)}"
    )


# ---------------------------------------------------------------------------
# create_analysis -- Q&A (event-specific) ΚΑΙ synthesis (negotiation_event_id=None)
# ---------------------------------------------------------------------------

def create_analysis(db: Session, data: NegotiationAnalysisCreate) -> NegotiationAnalysis:
    is_synthesis = data.negotiation_event_id is None

    if is_synthesis:
        context = _build_synthesis_context(db)
        system_prompt = SYSTEM_PROMPT_SYNTHESIS
    else:
        event = event_repository.get_by_id(db, data.negotiation_event_id)
        if event is None:
            raise EventForAnalysisNotFoundError(data.negotiation_event_id)
        context = _build_event_context(db, event)
        system_prompt = SYSTEM_PROMPT_QA

    user_message = _build_user_message(data.user_question, context)

    # Αν αυτό σηκώσει LLMCallError, ΔΕΝ φτάνουμε ποτέ στο analysis_repository.create --
    # άρα δεν αποθηκεύεται ποτέ μισή/άκυρη εγγραφή (βλ. main.py exception handler).
    result = llm_client.call_llm(system_prompt, user_message)

    analysis = NegotiationAnalysis(
        negotiation_event_id=data.negotiation_event_id,
        is_synthesis=is_synthesis,
        user_question=data.user_question,
        llm_answer=result["raw_text"],
        model_used=result["model"],
    )
    return analysis_repository.create(db, analysis)


# ---------------------------------------------------------------------------
# create_comparison -- σύγκριση ΑΚΡΙΒΩΣ δύο events, ίδιο LLM στρώμα με
# create_analysis παραπάνω, ξεχωριστό system prompt/context builder
# ---------------------------------------------------------------------------

def create_comparison(db: Session, event_a_id: int, event_b_id: int) -> NegotiationAnalysis:
    if event_a_id == event_b_id:
        raise IdenticalComparisonEventsError(event_a_id)

    event_a = event_repository.get_by_id(db, event_a_id)
    if event_a is None:
        raise EventForAnalysisNotFoundError(event_a_id)

    event_b = event_repository.get_by_id(db, event_b_id)
    if event_b is None:
        raise EventForAnalysisNotFoundError(event_b_id)

    context = _build_compare_context(db, event_a, event_b)
    user_message = _build_compare_message(context)

    # Ίδια εγγύηση με το create_analysis: LLMCallError -> καμία αποθήκευση.
    result = llm_client.call_llm(SYSTEM_PROMPT_COMPARE, user_message)

    # negotiation_event_id=event_a_id (όχι NULL+is_synthesis=True): το
    # is_synthesis σημαίνει "πάνω σε ΟΛΑ τα events", όχι "πάνω σε 2 events",
    # άρα θα ήταν παραπλανητικό. Με event_a_id ως FK η εγγραφή εμφανίζεται
    # στο GET /negotiation-analyses/by-event/{event_a_id}· το event_b_id
    # μπαίνει ρητά στο user_question ώστε να μείνει ανιχνεύσιμο χωρίς
    # migration για δεύτερη FK στήλη.
    analysis = NegotiationAnalysis(
        negotiation_event_id=event_a_id,
        is_synthesis=False,
        user_question=f"[COMPARE] Event {event_a_id} vs Event {event_b_id}",
        llm_answer=result["raw_text"],
        model_used=result["model"],
    )
    return analysis_repository.create(db, analysis)
