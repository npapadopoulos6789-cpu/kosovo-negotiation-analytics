import pytest
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
    # Serbia: 70 -> 50 (πτώση 20), Kosovo: 60 -> 45 (πτώση 15)
    # avg_decline = 17.5, / 30 * 100 = 58.33
    result = analytics_service.calculate_trend_score(
        current_serbia=50.0, previous_serbia=70.0,
        current_kosovo=45.0, previous_kosovo=60.0,
    )
    assert result == 58.33


def test_calculate_trend_score_ignores_increase():
    # Serbia ΑΥΞΗΘΗΚΕ (δεν μετράει ως "decline", γίνεται 0)
    # Kosovo έπεσε 10 -> avg_decline = 5, /30*100 = 16.67
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

    # symmetry = 100-20=80, trend=0 (no previous_year), social=60
    # 80*0.5 + 0*0.3 + 60*0.2 = 40 + 0 + 12 = 52
    assert result == 52.0


def test_calculate_window_score_returns_none_if_gap_missing(monkeypatch):
    monkeypatch.setattr(analytics_service, "calculate_power_gap", lambda db, s, k, y: None)

    result = analytics_service.calculate_window_score(
        db=None, serbia_id=1, kosovo_id=2, year=2013
    )

    assert result is None