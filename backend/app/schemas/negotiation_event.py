from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.negotiation_event import (
    ZopaSize, RipenessStatus, NegotiationType, ParticipantRole
)


class ParticipantCreate(BaseModel):
    """Ένας participant, όπως τον στέλνει ο χρήστης κατά τη δημιουργία event."""
    country_id: int
    role: ParticipantRole
    # Μόνο για role=SUPPORTER: ποιον δρώντα στηρίζει. None για τους
    # υπόλοιπους ρόλους (δεν βγάζει νόημα η έννοια "υποστηρίζει").
    supports_country_id: Optional[int] = None


class ParticipantRead(BaseModel):
    """Ένας participant, όπως τον επιστρέφουμε -- εμπλουτισμένο με το
    όνομα της χώρας, ώστε το frontend να μην χρειάζεται επιπλέον call."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    country_id: int
    country_name: str    # ΔΕΝ υπάρχει τέτοιο πεδίο στο model -- θα το
                          # "φτιάξουμε" στο service, βλ. παρακάτω
    role: ParticipantRole
    supports_country_id: Optional[int] = None


class NegotiationEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    date: date
    description: Optional[str] = None

    zopa_size: Optional[ZopaSize] = None
    zopa_reasoning: Optional[str] = None
    ripeness_status: Optional[RipenessStatus] = None
    ripeness_reasoning: Optional[str] = None
    batna_side_a: Optional[str] = None
    batna_side_b: Optional[str] = None
    red_lines_side_a: Optional[str] = None
    red_lines_side_b: Optional[str] = None
    negotiation_type: Optional[NegotiationType] = None

    economic_weight: int = 4
    military_weight: int = 4
    social_weight: int = 2

    implementation_success: Optional[float] = None


class NegotiationEventCreate(NegotiationEventBase):
    # Μια ΛΙΣΤΑ από participants, μέσα στο ίδιο request -- π.χ.
    # [{"country_id": 1, "role": "PARTY"}, {"country_id": 3, "role": "MEDIATOR"}]
    participants: list[ParticipantCreate] = []


class NegotiationEventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    date: Optional[date] = None
    description: Optional[str] = None
    zopa_size: Optional[ZopaSize] = None
    zopa_reasoning: Optional[str] = None
    ripeness_status: Optional[RipenessStatus] = None
    ripeness_reasoning: Optional[str] = None
    batna_side_a: Optional[str] = None
    batna_side_b: Optional[str] = None
    red_lines_side_a: Optional[str] = None
    red_lines_side_b: Optional[str] = None
    negotiation_type: Optional[NegotiationType] = None
    economic_weight: Optional[int] = None
    military_weight: Optional[int] = None
    social_weight: Optional[int] = None
    implementation_success: Optional[float] = None
    # Αν σταλεί, ΑΝΤΙΚΑΘΙΣΤΑ όλη τη λίστα participants (απλούστερο από
    # partial add/remove -- το documentάρουμε ρητά στο README αργότερα)
    participants: Optional[list[ParticipantCreate]] = None


class NegotiationEventRead(NegotiationEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    participants: list[ParticipantRead] = []