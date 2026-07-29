from sqlalchemy import Column, Integer, String, Date, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ZopaSize(str, enum.Enum):
    NARROW = "NARROW"
    MODERATE = "MODERATE"
    WIDE = "WIDE"


class RipenessStatus(str, enum.Enum):
    NOT_RIPE = "NOT_RIPE"
    EMERGING = "EMERGING"
    RIPE = "RIPE"


class NegotiationType(str, enum.Enum):
    DISTRIBUTIVE = "DISTRIBUTIVE"
    INTEGRATIVE_WIN_WIN = "INTEGRATIVE_WIN_WIN"


class ParticipantRole(str, enum.Enum):
    PARTY = "PARTY"
    MEDIATOR = "MEDIATOR"
    GUARANTOR = "GUARANTOR"


class NegotiationEvent(Base):
    __tablename__ = "negotiation_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)

    # Όλα προαιρετικά στο επίπεδο ΒΔ (ευελιξία στο workflow) -- αλλά στο
    # seed script θα τα συμπληρώσουμε ΟΛΑ, αφού είναι ο πυρήνας της
    # ακαδημαϊκής αξίας του project
    zopa_size = Column(Enum(ZopaSize), nullable=True)
    zopa_reasoning = Column(Text, nullable=True)
    ripeness_status = Column(Enum(RipenessStatus), nullable=True)
    ripeness_reasoning = Column(Text, nullable=True)
    batna_side_a = Column(Text, nullable=True)
    batna_side_b = Column(Text, nullable=True)
    red_lines_side_a = Column(Text, nullable=True)
    red_lines_side_b = Column(Text, nullable=True)
    negotiation_type = Column(Enum(NegotiationType), nullable=True)

    # Προεπιλογή 4/4/2 -- ο κανόνας "άθροισμα == 10" επιβάλλεται στο
    # SERVICE layer, ΚΑΙ σε create ΚΑΙ σε update (βλ. services/negotiation_event.py)
    economic_weight = Column(Integer, nullable=False, default=4)
    military_weight = Column(Integer, nullable=False, default=4)
    social_weight = Column(Integer, nullable=False, default=2)

    # cascade="all, delete-orphan": αν διαγράψουμε ένα event, διαγράφονται
    # αυτόματα και όλοι οι participants του -- δεν μένουν "ορφανές" γραμμές
    participants = relationship(
        "EventParticipant", back_populates="event", cascade="all, delete-orphan"
    )


class EventParticipant(Base):
    __tablename__ = "event_participants"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("negotiation_events.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    role = Column(Enum(ParticipantRole), nullable=False)

    event = relationship("NegotiationEvent", back_populates="participants")
    # Σύνδεση και προς το Country -- έτσι μπορούμε εύκολα να διαβάσουμε
    # participant.country.name χωρίς επιπλέον query
    country = relationship("Country")

    @property
    def country_name(self) -> str:
        return self.country.name