from sqlalchemy import Column, Integer, String, Float, Enum, Boolean, ForeignKey
import enum

from app.core.database import Base


class IndicatorCategory(str, enum.Enum):
    ECONOMIC = "ECONOMIC"
    MILITARY = "MILITARY"
    SOCIAL_UNREST = "SOCIAL_UNREST"


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)

    # ForeignKey("countries.id") λέει στη ΒΔ: "αυτό το πεδίο ΠΡΕΠΕΙ να δείχνει
    # σε μια πραγματική, υπάρχουσα γραμμή στον πίνακα countries -- δεν επιτρέπεται
    # να βάλεις εδώ ένα id χώρας που δεν υπάρχει"
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)

    # Enum: επιτρέπει μόνο μία από τις 3 κατηγορίες
    category = Column(Enum(IndicatorCategory), nullable=False)

    # π.χ. "GDP_growth", "unemployment_rate", "troop_presence", "freedom_house_score"
    indicator_type = Column(String(100), nullable=False)

    year = Column(Integer, nullable=False)

    # Float αντί για Integer, γιατί οι τιμές μπορεί να έχουν δεκαδικά (π.χ. 3.7%)
    value = Column(Float, nullable=False)

    # π.χ. "%", "index_score" -- προαιρετικό πεδίο (nullable=True)
    unit = Column(String(20), nullable=True)

    # π.χ. "IMF, 2024" -- η πηγή του δεδομένου, για διαφάνεια/ακαδημαϊκή αξιοπιστία
    source = Column(String(200), nullable=True)

    # Αν το δεδομένο έχει επιβεβαιωθεί χειροκίνητα (seed data της διπλωματικής = True)
    is_verified = Column(Boolean, nullable=False, default=True)