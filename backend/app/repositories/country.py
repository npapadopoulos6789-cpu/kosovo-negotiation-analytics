from sqlalchemy.orm import Session

from app.models.country import Country


def get_all(db: Session) -> list[Country]:
    return db.query(Country).order_by(Country.id).all()


def get_by_id(db: Session, country_id: int) -> Country | None:
    return db.query(Country).filter(Country.id == country_id).first()


def get_by_name(db: Session, name: str) -> Country | None:
    return db.query(Country).filter(Country.name == name).first()


def create(db: Session, country: Country) -> Country:
    db.add(country)
    db.commit()
    db.refresh(country)
    return country


def update(db: Session, country: Country, data: dict) -> Country:
    for field, value in data.items():
        setattr(country, field, value)
    db.commit()
    db.refresh(country)
    return country


def delete(db: Session, country: Country) -> None:
    db.delete(country)
    db.commit()
