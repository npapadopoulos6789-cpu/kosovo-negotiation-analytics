"""
Υπολογιστικός πυρήνας: Power Index, Power Gap, Window Score, Optimal
Periods, Best Moments. ΚΑΝΕΝΑΣ υπολογισμός εδώ δεν καλεί LLM -- όλα
είναι ντετερμινιστικά, ίδιο input δίνει πάντα ίδιο output.
"""
from sqlalchemy.orm import Session

from app.repositories import indicator as indicator_repository
from app.repositories import negotiation_event as event_repository


NORMALIZATION_RANGES = {
    "GDP_growth": (-20.0, 10.0),
    "freedom_house_score": (0.0, 100.0),
    "troop_presence_index": (0.0, 100.0),
}


def normalize(value: float, indicator_type: str) -> float:
    """
    Μετατρέπει μια "ωμή" τιμή σε κλίμακα 0-100, βάσει προκαθορισμένων
    ορίων min/max.
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
    Μέσος όρος normalized τιμών όλων των Indicators μιας κατηγορίας,
    για μια χώρα σε ένα έτος. None αν δεν υπάρχουν δεδομένα.
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


POWER_INDEX_WEIGHTS = {
    "ECONOMIC": 0.40,
    "MILITARY": 0.40,
    "SOCIAL_UNREST": 0.20,
}


def calculate_power_index(db: Session, country_id: int, year: int) -> float | None:
    """
    Συνδυάζει τα 3 category scores μιας χώρας σε ένα έτος, με τα
    σταθερά βάρη 40/40/20. None αν λείπει έστω μία κατηγορία.
    """
    economic = get_category_score(db, country_id, year, "ECONOMIC")
    military = get_category_score(db, country_id, year, "MILITARY")
    social = get_category_score(db, country_id, year, "SOCIAL_UNREST")

    if economic is None or military is None or social is None:
        return None

    power_index = (
        economic * POWER_INDEX_WEIGHTS["ECONOMIC"]
        + military * POWER_INDEX_WEIGHTS["MILITARY"]
        + social * POWER_INDEX_WEIGHTS["SOCIAL_UNREST"]
    )
    return round(power_index, 2)