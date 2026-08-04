# app/schemas/negotiation_analysis.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NegotiationAnalysisCreate(BaseModel):
    """
    Τι στέλνει ο χρήστης όταν ζητάει ανάλυση.
    Αν negotiation_event_id είναι None, σημαίνει ότι ζητάει synthesis
    (γενική ανάλυση πάνω σε όλα τα events μαζί).
    """
    negotiation_event_id: Optional[int] = None
    user_question: str


class SynthesisCreate(BaseModel):
    """Ό,τι στέλνει ο χρήστης στο POST /synthesis -- πάντα synthesis,
    άρα δεν χρειάζεται καν πεδίο negotiation_event_id."""
    user_question: str


class CompareCreate(BaseModel):
    """Ό,τι στέλνει ο χρήστης στο POST /compare -- ΑΚΡΙΒΩΣ δύο event_ids,
    καμία free-text ερώτηση (το task είναι πάντα το ίδιο: εξήγησε τη
    διαφορά τους)."""
    event_a_id: int
    event_b_id: int


class NegotiationAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    negotiation_event_id: Optional[int]
    is_synthesis: bool
    user_question: str
    llm_answer: Optional[str]
    model_used: Optional[str]
    created_at: datetime