from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.indicator import IndicatorCategory, IndicatorConfidence


class IndicatorBase(BaseModel):
    country_id: int
    category: IndicatorCategory
    indicator_type: str = Field(..., min_length=1, max_length=100)
    year: int
    value: float
    unit: Optional[str] = Field(None, max_length=20)
    source: Optional[str] = Field(None, max_length=200)
    is_verified: bool = True
    confidence: Optional[IndicatorConfidence] = None


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorUpdate(BaseModel):
    # Όλα προαιρετικά -- ο χρήστης στέλνει μόνο ό,τι θέλει να αλλάξει
    country_id: Optional[int] = None
    category: Optional[IndicatorCategory] = None
    indicator_type: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = None
    value: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=20)
    source: Optional[str] = Field(None, max_length=200)
    is_verified: Optional[bool] = None
    confidence: Optional[IndicatorConfidence] = None


class IndicatorRead(IndicatorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int