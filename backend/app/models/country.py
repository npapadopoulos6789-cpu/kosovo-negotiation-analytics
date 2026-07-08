from sqlalchemy import Column, Integer, String, Boolean, Enum
import enum

from app.core.database import Base


class ActorType(str, enum.Enum):
    STATE = "STATE"
    INTERNATIONAL_ORG = "INTERNATIONAL_ORG"
    MILITARY_ALLIANCE = "MILITARY_ALLIANCE"


class GeopoliticalBloc(str, enum.Enum):
    WEST = "WEST"
    EAST = "EAST"
    EU = "EU"
    NEUTRAL = "NEUTRAL"


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    actor_type = Column(Enum(ActorType), nullable=False, default=ActorType.STATE)
    geopolitical_bloc = Column(Enum(GeopoliticalBloc), nullable=True)
    recognized_kosovo = Column(Boolean, nullable=True)
    country_code = Column(String(3), nullable=True)