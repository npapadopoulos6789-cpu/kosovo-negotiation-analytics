from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.country import router as country_router
from app.api.indicator import router as indicator_router
from app.api.negotiation_event import router as negotiation_event_router
from app.api.auth import router as auth_router
from app.api.negotiation_analysis import router as negotiation_analysis_router
from app.api.analytics import router as analytics_router
from app.api.synthesis import router as synthesis_router
from app.api.compare import router as compare_router
from app.services.country import CountryNotFoundError, DuplicateCountryNameError
from app.services.indicator import IndicatorNotFoundError, CountryForIndicatorNotFoundError
from app.services.negotiation_event import (
    NegotiationEventNotFoundError, InvalidWeightsError, CountryForParticipantNotFoundError
)
from app.services.user import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.services.negotiation_analysis import (
    NegotiationAnalysisNotFoundError, EventForAnalysisNotFoundError, IdenticalComparisonEventsError
)
from app.services.llm_client import LLMCallError

app = FastAPI()

# Επιτρέπει στο React dev server (:5173) να καλεί αυτό το API (:8000) --
# χωρίς αυτό ο browser μπλοκάρει τα requests πριν καν φτάσουν στο FastAPI
# (browser-level block, όχι network error στο backend log).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

app.include_router(country_router)
app.include_router(indicator_router)
app.include_router(negotiation_event_router)
app.include_router(auth_router)
app.include_router(negotiation_analysis_router)
app.include_router(analytics_router)
app.include_router(synthesis_router)
app.include_router(compare_router)


@app.exception_handler(CountryNotFoundError)
def handle_country_not_found(request: Request, exc: CountryNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DuplicateCountryNameError)
def handle_duplicate_country_name(request: Request, exc: DuplicateCountryNameError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(IndicatorNotFoundError)
def handle_indicator_not_found(request: Request, exc: IndicatorNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(CountryForIndicatorNotFoundError)
def handle_country_for_indicator_not_found(request: Request, exc: CountryForIndicatorNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(NegotiationEventNotFoundError)
def handle_event_not_found(request: Request, exc: NegotiationEventNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidWeightsError)
def handle_invalid_weights(request: Request, exc: InvalidWeightsError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(CountryForParticipantNotFoundError)
def handle_country_for_participant_not_found(request: Request, exc: CountryForParticipantNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(EmailAlreadyRegisteredError)
def handle_email_already_registered(request: Request, exc: EmailAlreadyRegisteredError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidCredentialsError)
def handle_invalid_credentials(request: Request, exc: InvalidCredentialsError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(NegotiationAnalysisNotFoundError)
def handle_analysis_not_found(request: Request, exc: NegotiationAnalysisNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(EventForAnalysisNotFoundError)
def handle_event_for_analysis_not_found(request: Request, exc: EventForAnalysisNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(IdenticalComparisonEventsError)
def handle_identical_comparison_events(request: Request, exc: IdenticalComparisonEventsError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(LLMCallError)
def handle_llm_call_error(request: Request, exc: LLMCallError) -> JSONResponse:
    # 502: το δικό μας API δούλεψε σωστά, απέτυχε το upstream (Anthropic) call
    # ή η απάντησή του δεν ήταν έγκυρο JSON -- καμία εγγραφή δεν αποθηκεύτηκε.
    return JSONResponse(status_code=502, content={"detail": exc.message})


@app.get("/")
def read_root():
    return {"message": "Kosovo Negotiation Analytics API is running"}