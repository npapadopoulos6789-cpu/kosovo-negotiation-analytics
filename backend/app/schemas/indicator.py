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
    # Υποχρεωτικό (όχι Optional) -- κάθε indicator πρέπει να δηλώνει από πού
    # προέρχεται, για διαφάνεια/ακαδημαϊκή αξιοπιστία (δεν επιβάλλουμε ρητό
    # whitelist οργανισμών εδώ, βλ. IndicatorCreate.is_verified παρακάτω).
    source: str = Field(..., min_length=1, max_length=200)
    is_verified: bool = True
    confidence: Optional[IndicatorConfidence] = None


class IndicatorCreate(IndicatorBase):
    # Business rule: κάθε ΝΕΟ indicator (μέσω API, όχι seed) μπαίνει πάντα
    # is_verified=False, ανεξαρτήτως του τι δηλώνει ο ADMIN στο `source` --
    # δεν κάνουμε hard whitelist "αναγνωρισμένων οργανισμών" (θα εμπόδιζε
    # μελλοντικές μελέτες περίπτωσης με νόμιμες αλλά άγνωστες πηγές, βλ.
    # README "Beyond this case study"), απλά ΔΕΝ εμπιστευόμαστε αυτόματα
    # καμία νέα πηγή. Η μόνη οδός προς is_verified=True είναι ρητό
    # PUT /indicators/{id} από ADMIN, ίδιο μηχανισμό με το verify workflow
    # που ήδη περιγράφει το CLAUDE.md για μελλοντικά auto-fetched δεδομένα.
    # Το seed.py δεν επηρεάζεται -- override-άρει is_verified ρητά ανά
    # εγγραφή (True), δεν βασίζεται σε αυτό το default.
    is_verified: bool = False


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