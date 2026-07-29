from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.country import router as country_router
from app.api.indicator import router as indicator_router
from app.api.negotiation_event import router as negotiation_event_router
from app.services.country import CountryNotFoundError, DuplicateCountryNameError
from app.services.indicator import IndicatorNotFoundError, CountryForIndicatorNotFoundError
from app.services.negotiation_event import (
    NegotiationEventNotFoundError, InvalidWeightsError, CountryForParticipantNotFoundError
)

app = FastAPI()

app.include_router(country_router)
app.include_router(indicator_router)
app.include_router(negotiation_event_router)


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


@app.get("/")
def read_root():
    return {"message": "Kosovo Negotiation Analytics API is running"}