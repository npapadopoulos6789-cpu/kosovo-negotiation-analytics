from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.services import indicator as indicator_service
from app.schemas.indicator import IndicatorCreate, IndicatorUpdate, IndicatorRead

router = APIRouter(prefix="/indicators", tags=["Indicators"])


@router.get("/", response_model=list[IndicatorRead])
def list_indicators(db: Session = Depends(get_db)):
    return indicator_service.list_indicators(db)


@router.get("/{indicator_id}", response_model=IndicatorRead)
def get_indicator(indicator_id: int, db: Session = Depends(get_db)):
    # Σημείωσε: ΔΕΝ κάνουμε εδώ try/except -- αν πεταχτεί
    # IndicatorNotFoundError, το πιάνει αυτόματα ο exception handler
    # που θα προσθέσουμε στο main.py
    return indicator_service.get_indicator(db, indicator_id)


@router.get("/by-country/{country_id}", response_model=list[IndicatorRead])
def list_indicators_by_country(country_id: int, db: Session = Depends(get_db)):
    return indicator_service.list_indicators_by_country(db, country_id)


@router.post("/", response_model=IndicatorRead, status_code=201)
def create_indicator(
    payload: IndicatorCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    return indicator_service.create_indicator(db, payload)


@router.put("/{indicator_id}", response_model=IndicatorRead)
def update_indicator(
    indicator_id: int,
    payload: IndicatorUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    return indicator_service.update_indicator(db, indicator_id, payload)


@router.delete("/{indicator_id}", status_code=204)
def delete_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    indicator_service.delete_indicator(db, indicator_id)