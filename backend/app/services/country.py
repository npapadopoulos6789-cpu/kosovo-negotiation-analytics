from sqlalchemy.orm import Session

from app.models.country import Country
from app.repositories import country as country_repository
from app.schemas.country import CountryCreate, CountryUpdate


class CountryNotFoundError(Exception):
    def __init__(self, country_id: int):
        self.country_id = country_id
        super().__init__(f"Country {country_id} not found")


class DuplicateCountryNameError(Exception):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Country with name '{name}' already exists")


def list_countries(db: Session) -> list[Country]:
    return country_repository.get_all(db)


def get_country(db: Session, country_id: int) -> Country:
    country = country_repository.get_by_id(db, country_id)
    if country is None:
        raise CountryNotFoundError(country_id)
    return country


def create_country(db: Session, data: CountryCreate) -> Country:
    if country_repository.get_by_name(db, data.name) is not None:
        raise DuplicateCountryNameError(data.name)
    country = Country(**data.model_dump())
    return country_repository.create(db, country)


def update_country(db: Session, country_id: int, data: CountryUpdate) -> Country:
    country = get_country(db, country_id)

    update_data = data.model_dump(exclude_unset=True)
    new_name = update_data.get("name")
    if new_name is not None and new_name != country.name:
        if country_repository.get_by_name(db, new_name) is not None:
            raise DuplicateCountryNameError(new_name)

    return country_repository.update(db, country, update_data)


def delete_country(db: Session, country_id: int) -> None:
    country = get_country(db, country_id)
    country_repository.delete(db, country)
