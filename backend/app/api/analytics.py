from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import analytics as analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/power-index/{country_id}/{year}")
def get_power_index(country_id: int, year: int, db: Session = Depends(get_db)):
    result = analytics_service.calculate_power_index(db, country_id, year)
    if result is None:
        raise HTTPException(status_code=404, detail="Insufficient data for this country/year")
    return {"country_id": country_id, "year": year, "power_index": result}


@router.get("/power-index-breakdown/{country_id}/{year}")
def get_power_index_breakdown(country_id: int, year: int, db: Session = Depends(get_db)):
    result = analytics_service.calculate_power_index_breakdown(db, country_id, year)
    if result is None:
        raise HTTPException(status_code=404, detail="Insufficient data for this country/year")
    return {"country_id": country_id, "year": year, **result}


@router.get("/power-gap/{year}")
def get_power_gap(
    year: int, serbia_id: int, kosovo_id: int, db: Session = Depends(get_db)
):
    result = analytics_service.calculate_power_gap(db, serbia_id, kosovo_id, year)
    if result is None:
        raise HTTPException(status_code=404, detail="Insufficient data")
    return {"year": year, "power_gap": result}


@router.get("/window-score/{year}")
def get_window_score(
    year: int,
    serbia_id: int,
    kosovo_id: int,
    previous_year: int | None = None,
    db: Session = Depends(get_db),
):
    if previous_year is None and year in analytics_service.KEY_YEARS:
        previous_year = analytics_service._most_recent_year_with_data(
            db, serbia_id, kosovo_id, year
        )
    result = analytics_service.calculate_window_score(db, serbia_id, kosovo_id, year, previous_year)
    if result is None:
        raise HTTPException(status_code=404, detail="Insufficient data")
    return {"year": year, "window_score": result}


@router.get("/optimal-agreement-period/{country_id}")
def get_optimal_agreement_period(country_id: int, db: Session = Depends(get_db)):
    result = analytics_service.find_optimal_agreement_period(db, country_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Insufficient data")
    return result


@router.get("/optimal-mutual-compromise")
def get_optimal_mutual_compromise(
    serbia_id: int, kosovo_id: int, db: Session = Depends(get_db)
):
    result = analytics_service.find_optimal_mutual_compromise_period(db, serbia_id, kosovo_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Insufficient data")
    return result


@router.get("/best-moments")
def get_best_moments(serbia_id: int, kosovo_id: int, db: Session = Depends(get_db)):
    return analytics_service.find_best_moments(db, serbia_id, kosovo_id)