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
    "unemployment_rate": (0.0, 60.0),
    "trade_share_eu": (0.0, 100.0),
    "military_expenditure_pct_gdp": (0.0, 8.0),
}


def normalize(value: float, indicator_type: str) -> float:
    if indicator_type not in NORMALIZATION_RANGES:
        raise ValueError(f"Δεν υπάρχουν normalization όρια για '{indicator_type}'")

    min_val, max_val = NORMALIZATION_RANGES[indicator_type]
    clamped = max(min_val, min(value, max_val))
    normalized = (clamped - min_val) / (max_val - min_val) * 100
    return round(normalized, 2)


def get_category_score(
    db: Session, country_id: int, year: int, category: str
) -> float | None:
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


def calculate_power_gap(
    db: Session, serbia_id: int, kosovo_id: int, year: int
) -> float | None:
    serbia_pi = calculate_power_index(db, serbia_id, year)
    kosovo_pi = calculate_power_index(db, kosovo_id, year)

    if serbia_pi is None or kosovo_pi is None:
        return None

    return round(abs(serbia_pi - kosovo_pi), 2)


def calculate_trend_score(
    current_serbia: float, previous_serbia: float,
    current_kosovo: float, previous_kosovo: float,
) -> float:
    serbia_decline = max(0.0, previous_serbia - current_serbia)
    kosovo_decline = max(0.0, previous_kosovo - current_kosovo)
    avg_decline = (serbia_decline + kosovo_decline) / 2
    return round(min(100.0, avg_decline / 30 * 100), 2)


def calculate_social_pressure_score(
    db: Session, serbia_id: int, kosovo_id: int, year: int
) -> float | None:
    serbia_social = get_category_score(db, serbia_id, year, "SOCIAL_UNREST")
    kosovo_social = get_category_score(db, kosovo_id, year, "SOCIAL_UNREST")

    if serbia_social is None or kosovo_social is None:
        return None

    avg_stability = (serbia_social + kosovo_social) / 2
    return round(100 - avg_stability, 2)


def calculate_window_score(
    db: Session,
    serbia_id: int,
    kosovo_id: int,
    year: int,
    previous_year: int | None = None,
) -> float | None:
    gap = calculate_power_gap(db, serbia_id, kosovo_id, year)
    if gap is None:
        return None
    symmetry_score = round(100 - gap, 2)

    trend_score = 0.0
    if previous_year is not None:
        current_serbia = calculate_power_index(db, serbia_id, year)
        previous_serbia = calculate_power_index(db, serbia_id, previous_year)
        current_kosovo = calculate_power_index(db, kosovo_id, year)
        previous_kosovo = calculate_power_index(db, kosovo_id, previous_year)

        if None not in (current_serbia, previous_serbia, current_kosovo, previous_kosovo):
            trend_score = calculate_trend_score(
                current_serbia, previous_serbia, current_kosovo, previous_kosovo
            )

    social_pressure = calculate_social_pressure_score(db, serbia_id, kosovo_id, year)
    if social_pressure is None:
        return None

    window_score = (
        symmetry_score * 0.50
        + trend_score * 0.30
        + social_pressure * 0.20
    )
    return round(window_score, 2)


KEY_YEARS = [1998, 1999, 2000, 2005, 2007, 2008, 2013, 2018, 2020, 2023]


def find_optimal_agreement_period(db: Session, country_id: int) -> dict | None:
    best_year = None
    best_score = None

    for year in KEY_YEARS:
        score = calculate_power_index(db, country_id, year)
        if score is None:
            continue
        if best_score is None or score > best_score:
            best_score = score
            best_year = year

    if best_year is None:
        return None

    return {"year": best_year, "power_index": best_score}


def find_optimal_mutual_compromise_period(
    db: Session, serbia_id: int, kosovo_id: int
) -> dict | None:
    best_year = None
    best_score = None
    previous_year = None

    for year in KEY_YEARS:
        score = calculate_window_score(db, serbia_id, kosovo_id, year, previous_year)
        previous_year = year

        if score is None:
            continue
        if best_score is None or score > best_score:
            best_score = score
            best_year = year

    if best_year is None:
        return None

    return {"year": best_year, "window_score": best_score}


BEST_MOMENT_THRESHOLD = 60.0


def find_best_moments(db: Session, serbia_id: int, kosovo_id: int) -> list[dict]:
    events = event_repository.get_all(db)
    results = []

    for event in events:
        year = event.date.year
        if year not in KEY_YEARS:
            continue

        qualitative_positive = (
            (event.ripeness_status is not None and event.ripeness_status.value == "RIPE")
            or (event.zopa_size is not None and event.zopa_size.value == "WIDE")
        )

        idx = KEY_YEARS.index(year)
        prev = KEY_YEARS[idx - 1] if idx > 0 else None
        window_score = calculate_window_score(db, serbia_id, kosovo_id, year, prev)
        quantitative_positive = (
            window_score is not None and window_score >= BEST_MOMENT_THRESHOLD
        )

        if qualitative_positive and quantitative_positive:
            confidence = "HIGH"
        elif qualitative_positive or quantitative_positive:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        results.append({
            "event_id": event.id,
            "title": event.title,
            "year": year,
            "qualitative_positive": qualitative_positive,
            "window_score": window_score,
            "confidence": confidence,
        })

    return results