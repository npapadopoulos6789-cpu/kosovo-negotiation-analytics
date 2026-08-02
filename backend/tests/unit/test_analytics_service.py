import pytest
from datetime import date
from unittest.mock import MagicMock

from app.models.indicator import Indicator
from app.services import analytics as analytics_service


def test_normalize_middle_value():
    result = analytics_service.normalize(2.6, "GDP_growth")
    assert result == 75.33


def test_normalize_clamps_below_minimum():
    result = analytics_service.normalize(-50.0, "GDP_growth")
    assert result == 0.0


def test_normalize_clamps_above_maximum():
    result = analytics_service.normalize(50.0, "GDP_growth")
    assert result == 100.0


def test_normalize_unknown_indicator_type_raises():
    with pytest.raises(ValueError):
        analytics_service.normalize(5.0, "unknown_type")


def make_fake_indicator(country_id, category, indicator_type, year, value):
    ind = MagicMock(spec=Indicator)
    ind.country_id = country_id
    ind.year = year
    ind.value = value
    ind.indicator_type = indicator_type
    ind.category = MagicMock()
    ind.category.value = category
    return ind


def test_get_category_score_averages_multiple_indicators(monkeypatch):
    fake_indicators = [
        make_fake_indicator(1, "ECONOMIC", "GDP_growth", 2013, 2.6),
    ]
    monkeypatch.setattr(
        analytics_service.indicator_repository, "get_by_country",
        lambda db, country_id: fake_indicators
    )

    result = analytics_service.get_category_score(db=None, country_id=1, year=2013, category="ECONOMIC")

    assert result == 75.33


def test_get_category_score_returns_none_when_no_data(monkeypatch):
    monkeypatch.setattr(
        analytics_service.indicator_repository, "get_by_country",
        lambda db, country_id: []
    )

    result = analytics_service.get_category_score(db=None, country_id=1, year=2013, category="MILITARY")

    assert result is None


def test_calculate_power_index_combines_categories(monkeypatch):
    def fake_get_category_score(db, country_id, year, category):
        scores = {"ECONOMIC": 80.0, "MILITARY": 60.0, "SOCIAL_UNREST": 50.0}
        return scores[category]

    monkeypatch.setattr(analytics_service, "get_category_score", fake_get_category_score)

    result = analytics_service.calculate_power_index(db=None, country_id=1, year=2013)

    assert result == 66.0


def test_calculate_power_index_returns_none_if_category_missing(monkeypatch):
    def fake_get_category_score(db, country_id, year, category):
        if category == "MILITARY":
            return None
        return 80.0

    monkeypatch.setattr(analytics_service, "get_category_score", fake_get_category_score)

    result = analytics_service.calculate_power_index(db=None, country_id=1, year=2013)

    assert result is None


def test_calculate_power_gap_returns_absolute_difference(monkeypatch):
    def fake_power_index(db, country_id, year):
        return {1: 70.0, 2: 45.0}[country_id]

    monkeypatch.setattr(analytics_service, "calculate_power_index", fake_power_index)

    result = analytics_service.calculate_power_gap(db=None, serbia_id=1, kosovo_id=2, year=2013)

    assert result == 25.0


def test_calculate_power_gap_returns_none_if_missing_data(monkeypatch):
    def fake_power_index(db, country_id, year):
        return None if country_id == 2 else 70.0

    monkeypatch.setattr(analytics_service, "calculate_power_index", fake_power_index)

    result = analytics_service.calculate_power_gap(db=None, serbia_id=1, kosovo_id=2, year=2013)

    assert result is None


def test_calculate_trend_score_both_declining():
    result = analytics_service.calculate_trend_score(
        current_serbia=50.0, previous_serbia=70.0,
        current_kosovo=45.0, previous_kosovo=60.0,
    )
    assert result == 58.33


def test_calculate_trend_score_ignores_increase():
    result = analytics_service.calculate_trend_score(
        current_serbia=80.0, previous_serbia=70.0,
        current_kosovo=50.0, previous_kosovo=60.0,
    )
    assert result == 16.67


def test_calculate_window_score_without_previous_year(monkeypatch):
    monkeypatch.setattr(analytics_service, "calculate_power_gap", lambda db, s, k, y: 20.0)
    monkeypatch.setattr(
        analytics_service, "calculate_social_pressure_score", lambda db, s, k, y: 60.0
    )

    result = analytics_service.calculate_window_score(
        db=None, serbia_id=1, kosovo_id=2, year=2013, previous_year=None
    )

    assert result == 52.0


def test_calculate_window_score_returns_none_if_gap_missing(monkeypatch):
    monkeypatch.setattr(analytics_service, "calculate_power_gap", lambda db, s, k, y: None)

    result = analytics_service.calculate_window_score(
        db=None, serbia_id=1, kosovo_id=2, year=2013
    )

    assert result is None


def test_find_optimal_agreement_period_returns_best_year(monkeypatch):
    def fake_power_index(db, country_id, year):
        scores = {1999: 68.5, 2005: 55.0, 2013: 41.2, 2023: 50.0}
        return scores.get(year)

    monkeypatch.setattr(analytics_service, "calculate_power_index", fake_power_index)

    result = analytics_service.find_optimal_agreement_period(db=None, country_id=1)

    assert result == {"year": 1999, "power_index": 68.5}


def test_find_optimal_agreement_period_skips_missing_years(monkeypatch):
    def fake_power_index(db, country_id, year):
        return 60.0 if year == 2013 else None

    monkeypatch.setattr(analytics_service, "calculate_power_index", fake_power_index)

    result = analytics_service.find_optimal_agreement_period(db=None, country_id=1)

    assert result == {"year": 2013, "power_index": 60.0}


def test_find_optimal_agreement_period_returns_none_if_no_data(monkeypatch):
    monkeypatch.setattr(analytics_service, "calculate_power_index", lambda db, c, y: None)

    result = analytics_service.find_optimal_agreement_period(db=None, country_id=1)

    assert result is None


def test_find_optimal_mutual_compromise_period_returns_best_year(monkeypatch):
    scores = {1999: 40.0, 2005: 55.0, 2007: 50.0, 2008: 45.0, 2013: 82.3, 2023: 61.0}

    def fake_window_score(db, s, k, year, previous_year=None):
        return scores.get(year)

    # calculate_power_index χρειάζεται mock εδώ επειδή το
    # find_optimal_mutual_compromise_period το καλεί εσωτερικά (μέσω
    # _most_recent_year_with_data) για να βρει ένα σωστό previous_year --
    # η ίδια η τιμή δεν έχει σημασία σε αυτό το test, το fake_window_score
    # αγνοεί το previous_year και κοιτάει μόνο το year
    monkeypatch.setattr(analytics_service, "calculate_power_index", lambda db, c, y: 50.0)
    monkeypatch.setattr(analytics_service, "calculate_window_score", fake_window_score)

    result = analytics_service.find_optimal_mutual_compromise_period(db=None, serbia_id=1, kosovo_id=2)

    assert result == {"year": 2013, "window_score": 82.3}


def test_find_optimal_mutual_compromise_period_returns_none_if_no_data(monkeypatch):
    monkeypatch.setattr(analytics_service, "calculate_power_index", lambda db, c, y: None)
    monkeypatch.setattr(
        analytics_service, "calculate_window_score", lambda db, s, k, y, py=None: None
    )

    result = analytics_service.find_optimal_mutual_compromise_period(db=None, serbia_id=1, kosovo_id=2)

    assert result is None


def test_most_recent_year_with_data_skips_years_missing_either_countrys_data(monkeypatch):
    """
    Regression test για το bug (διορθώθηκε 2026-08-03): πριν τη διόρθωση,
    το find_optimal_mutual_compromise_period χρησιμοποιούσε σαν
    previous_year απλά το προηγούμενο στοιχείο της λίστας KEY_YEARS, ό,τι
    δεδομένα κι αν είχε -- με αραιά KEY_YEARS αυτό συχνά έπεφτε σε έτος
    χωρίς δεδομένα, μηδενίζοντας αθόρυβα το trend_score (30% βάρος στο
    Window Score). Εδώ: KEY_YEARS=[2005,2008,2013], το 2008 (αμέσως πριν
    το 2013) ΔΕΝ έχει δεδομένα, αλλά το 2005 έχει -- το previous_year
    για το 2013 πρέπει να είναι 2005, όχι 2008.
    """
    pi_values = {
        (1, 2005): 40.0, (2, 2005): 40.0,
        (1, 2008): None, (2, 2008): None,
        (1, 2013): 60.0, (2, 2013): 60.0,
    }
    monkeypatch.setattr(
        analytics_service, "calculate_power_index",
        lambda db, country_id, year: pi_values.get((country_id, year)),
    )

    used_previous_years = []

    def fake_window_score(db, s, k, year, previous_year=None):
        used_previous_years.append((year, previous_year))
        return {2005: 50.0, 2008: None, 2013: 70.0}.get(year)

    monkeypatch.setattr(analytics_service, "calculate_window_score", fake_window_score)
    monkeypatch.setattr(analytics_service, "KEY_YEARS", [2005, 2008, 2013])

    result = analytics_service.find_optimal_mutual_compromise_period(db=None, serbia_id=1, kosovo_id=2)

    assert result == {"year": 2013, "window_score": 70.0}
    assert (2013, 2005) in used_previous_years
    assert (2013, 2008) not in used_previous_years


def make_fake_event(id, title, event_date, ripeness_status=None, zopa_size=None):
    ev = MagicMock()
    ev.id = id
    ev.title = title
    ev.date = event_date
    if ripeness_status:
        ev.ripeness_status = MagicMock()
        ev.ripeness_status.value = ripeness_status
    else:
        ev.ripeness_status = None
    if zopa_size:
        ev.zopa_size = MagicMock()
        ev.zopa_size.value = zopa_size
    else:
        ev.zopa_size = None
    return ev


def test_find_best_moments_high_confidence_when_both_agree(monkeypatch):
    fake_events = [
        make_fake_event(1, "Brussels Agreement", date(2013, 4, 19), ripeness_status="RIPE", zopa_size="WIDE"),
    ]
    monkeypatch.setattr(analytics_service.event_repository, "get_all", lambda db: fake_events)
    # calculate_power_index χρειάζεται mock εδώ επειδή το find_best_moments
    # το καλεί εσωτερικά (μέσω _most_recent_year_with_data) για να βρει
    # ένα σωστό previous_year -- η τιμή δεν έχει σημασία σε αυτό το test
    monkeypatch.setattr(analytics_service, "calculate_power_index", lambda db, c, y: 50.0)
    monkeypatch.setattr(
        analytics_service, "calculate_window_score", lambda db, s, k, y, py=None: 82.3
    )

    result = analytics_service.find_best_moments(db=None, serbia_id=1, kosovo_id=2)

    assert len(result) == 1
    assert result[0]["confidence"] == "HIGH"
    assert result[0]["title"] == "Brussels Agreement"


def test_find_best_moments_low_confidence_when_neither_agree(monkeypatch):
    fake_events = [
        make_fake_event(1, "Rambouillet Talks", date(1999, 2, 6), ripeness_status="NOT_RIPE", zopa_size="NARROW"),
    ]
    monkeypatch.setattr(analytics_service.event_repository, "get_all", lambda db: fake_events)
    monkeypatch.setattr(analytics_service, "calculate_power_index", lambda db, c, y: 50.0)
    monkeypatch.setattr(
        analytics_service, "calculate_window_score", lambda db, s, k, y, py=None: 30.0
    )

    result = analytics_service.find_best_moments(db=None, serbia_id=1, kosovo_id=2)

    assert result[0]["confidence"] == "LOW"


def test_find_best_moments_skips_events_outside_key_years(monkeypatch):
    fake_events = [
        make_fake_event(1, "Some Event", date(2001, 1, 1)),
    ]
    monkeypatch.setattr(analytics_service.event_repository, "get_all", lambda db: fake_events)

    result = analytics_service.find_best_moments(db=None, serbia_id=1, kosovo_id=2)

    assert result == []