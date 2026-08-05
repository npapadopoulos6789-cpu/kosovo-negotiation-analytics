from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.country import ActorType, GeopoliticalBloc


class CountryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    actor_type: ActorType = ActorType.STATE
    geopolitical_bloc: Optional[GeopoliticalBloc] = None
    recognized_kosovo: Optional[bool] = None
    country_code: Optional[str] = Field(None, max_length=3)
    role_description: Optional[str] = None


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    actor_type: Optional[ActorType] = None
    geopolitical_bloc: Optional[GeopoliticalBloc] = None
    recognized_kosovo: Optional[bool] = None
    country_code: Optional[str] = Field(None, max_length=3)
    role_description: Optional[str] = None


class CountryRead(CountryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
