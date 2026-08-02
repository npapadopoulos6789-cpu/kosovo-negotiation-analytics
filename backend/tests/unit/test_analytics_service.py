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