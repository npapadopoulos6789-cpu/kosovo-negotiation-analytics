from sqlalchemy.orm import Session

from app.models.indicator import Indicator
from app.repositories import indicator as indicator_repository
from app.repositories import country as country_repository
from app.schemas.indicator import IndicatorCreate, IndicatorUpdate


class IndicatorNotFoundError(Exception):
    def __init__(self, indicator_id: int):
        self.indicator_id = indicator_id
        super().__init__(f"Indicator {indicator_id} not found")


class CountryForIndicatorNotFoundError(Exception):
    # Ξεχωριστό exception από το CountryNotFoundError (του country.py) --
    # εδώ σημαίνει συγκεκριμένα "η χώρα που ζητήθηκε για ΑΥΤΟ το indicator
    # δεν υπάρχει", όχι γενικά "μια χώρα δεν βρέθηκε"
    def __init__(self, country_id: int):
        self.country_id = country_id
        super().__init__(f"Country {country_id} not found for indicator")


def list_indicators(db: Session) -> list[Indicator]:
    return indicator_repository.get_all(db)


def get_indicator(db: Session, indicator_id: int) -> Indicator:
    indicator = indicator_repository.get_by_id(db, indicator_id)
    if indicator is None:
        raise IndicatorNotFoundError(indicator_id)
    return indicator


def list_indicators_by_country(db: Session, country_id: int) -> list[Indicator]:
    return indicator_repository.get_by_country(db, country_id)


def create_indicator(db: Session, data: IndicatorCreate) -> Indicator:
    # Business rule: η χώρα που αναφέρεται πρέπει να υπάρχει πραγματικά
    if country_repository.get_by_id(db, data.country_id) is None:
        raise CountryForIndicatorNotFoundError(data.country_id)

    indicator = Indicator(**data.model_dump())
    return indicator_repository.create(db, indicator)


def update_indicator(db: Session, indicator_id: int, data: IndicatorUpdate) -> Indicator:
    indicator = get_indicator(db, indicator_id)

    update_data = data.model_dump(exclude_unset=True)
    new_country_id = update_data.get("country_id")
    if new_country_id is not None:
        if country_repository.get_by_id(db, new_country_id) is None:
            raise CountryForIndicatorNotFoundError(new_country_id)

    return indicator_repository.update(db, indicator, update_data)


def delete_indicator(db: Session, indicator_id: int) -> None:
    indicator = get_indicator(db, indicator_id)
    indicator_repository.delete(db, indicator)