from sqlalchemy.orm import Session

from app.models.indicator import Indicator


def get_all(db: Session) -> list[Indicator]:
    return db.query(Indicator).order_by(Indicator.id).all()


def get_by_id(db: Session, indicator_id: int) -> Indicator | None:
    return db.query(Indicator).filter(Indicator.id == indicator_id).first()


def get_by_country(db: Session, country_id: int) -> list[Indicator]:
    return db.query(Indicator).filter(Indicator.country_id == country_id).all()


def create(db: Session, indicator: Indicator) -> Indicator:
    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator


def update(db: Session, indicator: Indicator, data: dict) -> Indicator:
    for field, value in data.items():
        setattr(indicator, field, value)
    db.commit()
    db.refresh(indicator)
    return indicator


def delete(db: Session, indicator: Indicator) -> None:
    db.delete(indicator)
    db.commit()