"""
Υπολογιστικός πυρήνας: Power Index, Power Gap, Window Score, Optimal
Periods, Best Moments. ΚΑΝΕΝΑΣ υπολογισμός εδώ δεν καλεί LLM -- όλα
είναι ντετερμινιστικά, ίδιο input δίνει πάντα ίδιο output.
"""
from sqlalchemy.orm import Session

from app.repositories import indicator as indicator_repository
from app.repositories import negotiation_event as event_repository


# Σταθερά, τεκμηριωμένα όρια normalization ανά indicator_type.
# ΣΗΜΑΝΤΙΚΟ: αυτά είναι παραδοχές, όχι εμπειρικά εξαγόμενες τιμές --
# τεκμηριώνονται ρητά στο README, ενότητα "Methodology & Limitations".
NORMALIZATION_RANGES = {
    "GDP_growth": (-20.0, 10.0),            # % ετήσια μεταβολή
    "freedom_house_score": (0.0, 100.0),     # ήδη σε κλίμακα 0-100
    "troop_presence_index": (0.0, 100.0),     # ήδη σε κλίμακα 0-100
}


def normalize(value: float, indicator_type: str) -> float:
    """
    Μετατρέπει μια "ωμή" τιμή (π.χ. GDP growth = 2.6) σε κλίμακα 0-100,
    βάσει προκαθορισμένων ορίων min/max.
    """
    if indicator_type not in NORMALIZATION_RANGES:
        raise ValueError(f"Δεν υπάρχουν normalization όρια για '{indicator_type}'")

    min_val, max_val = NORMALIZATION_RANGES[indicator_type]

    clamped = max(min_val, min(value, max_val))
    normalized = (clamped - min_val) / (max_val - min_val) * 100
    return round(normalized, 2)


def get_category_score(
    db: Session, country_id: int, year: int, category: str
) -> float | None:
    """
    Επιστρέφει το μέσο όρο των normalized τιμών όλων των Indicators
    μιας συγκεκριμένης κατηγορίας (ECONOMIC/MILITARY/SOCIAL_UNREST),
    για μια χώρα σε ένα έτος.

    Επιστρέφει None αν δεν υπάρχει ΚΑΝΕΝΑ Indicator αυτής της
    κατηγορίας για αυτή τη χώρα/έτος -- δεν "μαντεύουμε" τιμή.
    """
    all_indicators = indicator_repository.get_by_country(db, country_id)

    matching = [
        ind for ind in all_indicators
        if ind.year == year and ind.category.value == category
    ]

    if not matching:
        return None

    normalized_values = [normalize(ind.value, ind.indicator_type) for ind in matching]
    average = sum(normalized_values) / len(normalized_values)
    return round(average, 2)