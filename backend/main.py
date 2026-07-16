from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.country import router as country_router
from app.services.country import CountryNotFoundError, DuplicateCountryNameError

app = FastAPI()

app.include_router(country_router)


@app.exception_handler(CountryNotFoundError)
def handle_country_not_found(request: Request, exc: CountryNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DuplicateCountryNameError)
def handle_duplicate_country_name(request: Request, exc: DuplicateCountryNameError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/")
def read_root():
    return {"message": "Kosovo Negotiation Analytics API is running"}