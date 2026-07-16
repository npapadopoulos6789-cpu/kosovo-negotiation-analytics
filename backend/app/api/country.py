from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.country import CountryCreate, CountryRead, CountryUpdate
from app.services import country as country_service

router = APIRouter(prefix="/countries", tags=["countries"])


@router.get("", response_model=list[CountryRead])
def list_countries(db: Session = Depends(get_db)):
    return country_service.list_countries(db)


@router.get("/{country_id}", response_model=CountryRead)
def get_country(country_id: int, db: Session = Depends(get_db)):
    return country_service.get_country(db, country_id)


@router.post("", response_model=CountryRead, status_code=status.HTTP_201_CREATED)
def create_country(payload: CountryCreate, db: Session = Depends(get_db)):
    return country_service.create_country(db, payload)


@router.put("/{country_id}", response_model=CountryRead)
def update_country(country_id: int, payload: CountryUpdate, db: Session = Depends(get_db)):
    return country_service.update_country(db, country_id, payload)


@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(country_id: int, db: Session = Depends(get_db)):
    country_service.delete_country(db, country_id)
