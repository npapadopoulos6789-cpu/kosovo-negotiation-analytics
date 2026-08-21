from sqlalchemy import Column, Integer, String, Float, Enum, Boolean, ForeignKey
import enum

from app.core.database import Base


class IndicatorCategory(str, enum.Enum):
    ECONOMIC = "ECONOMIC"
    MILITARY = "MILITARY"
    SOCIAL_UNREST = "SOCIAL_UNREST"


class IndicatorConfidence(str, enum.Enum):
    EXACT = "EXACT"              # ρητά αναφερόμενο στο κείμενο της πηγής
    CHART_READ = "CHART_READ"    # διαβασμένο από άξονα γραφήματος
    RANGE = "RANGE"               # η πηγή έδωσε εύρος, αποθηκεύσαμε μέσο όρο


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

    # π.χ. "IMF, 2024" -- η πηγή του δεδομένου, για διαφάνεια/ακαδημαϊκή αξιοπιστία.
    # nullable=False: κάθε indicator ΠΡΕΠΕΙ να δηλώνει πηγή -- επιβάλλεται ήδη
    # στο IndicatorBase schema, εδώ το κλειδώνουμε και σε επίπεδο ΒΔ ώστε να
    # μην μπορεί να παρακαμφθεί από κώδικα που γράφει απευθείας στη ΒΔ χωρίς
    # να περάσει από το schema.
    source = Column(String(200), nullable=False)

    # server_default=False (όχι True): "soft" έλεγχος πηγής -- δεν κρατάμε hard
    # whitelist αναγνωρισμένων οργανισμών (θα εμπόδιζε μελλοντικές μελέτες
    # περίπτωσης με νόμιμες αλλά άγνωστες πηγές, βλ. README "Beyond this case
    # study"), απλά ΔΕΝ εμπιστευόμαστε αυτόματα καμία νέα εγγραφή -- μόνο ρητό
    # PUT από ADMIN τη γυρίζει σε True (βλ. IndicatorCreate.is_verified). Το
    # seed.py δεν επηρεάζεται, περνάει is_verified=True ρητά ανά εγγραφή.
    is_verified = Column(Boolean, nullable=False, default=False, server_default="false")

    # nullable=True: όχι κάθε εγγραφή έχει νόημα να ταξινομηθεί ως EXACT/CHART_READ/
    # RANGE (π.χ. researcher estimates όπως το troop_presence_index δεν είναι
    # "διάβασμα πηγής"), οπότε δεν το κάνουμε υποχρεωτικό στο επίπεδο ΒΔ
    confidence = Column(Enum(IndicatorConfidence), nullable=True)