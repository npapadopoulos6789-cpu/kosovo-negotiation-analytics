from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class NegotiationAnalysis(Base):
    __tablename__ = "negotiation_analyses"

    id = Column(Integer, primary_key=True, index=True)

    # nullable=True: όταν είναι "synthesis" (γενική ανάλυση πάνω σε ΟΛΑ τα
    # events), δεν αφορά ΕΝΑ συγκεκριμένο event -- γι' αυτό επιτρέπουμε NULL
    negotiation_event_id = Column(
        Integer, ForeignKey("negotiation_events.id"), nullable=True
    )

    # True όταν είναι γενική σύνθεση (synthesis), False όταν είναι
    # ανάλυση πάνω σε συγκεκριμένο event
    is_synthesis = Column(Boolean, nullable=False, default=False)

    user_question = Column(Text, nullable=False)
    llm_answer = Column(Text, nullable=True)  # nullable: γεμίζει ΜΕΤΑ την κλήση στο LLM

    # Ποιο μοντέλο χρησιμοποιήθηκε -- π.χ. "gpt-4o-mini" -- για διαφάνεια
    model_used = Column(String(100), nullable=True)

    # timezone.utc: αποθηκεύουμε πάντα σε UTC, όχι τοπική ώρα -- καλή
    # πρακτική ώστε να μη μπερδευόμαστε αν η εφαρμογή "ταξιδέψει" σε
    # server με διαφορετική ζώνη ώρας
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    event = relationship("NegotiationEvent")