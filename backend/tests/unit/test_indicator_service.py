import pytest

from app.models.country import Country
from app.models.indicator import Indicator
from app.schemas.indicator import IndicatorCreate, IndicatorUpdate
from app.services import indicator as indicator_service
from app.services.indicator import IndicatorNotFoundError, CountryForIndicatorNotFoundError


class FakeIndicatorRepository:
    """In-memory αντικαταστάτης του app.repositories.indicator."""

    def __init__(self):
        self._indicators: dict[int, Indicator] = {}
        self._next_id = 1

    def get_all(self, db):
        return list(self._indicators.values())

    def get_by_id(self, db, indicator_id):
        return self._indicators.get(indicator_id)

    def get_by_country(self, db, country_id):
        return [i for i in self._indicators.values() if i.country_id == country_id]

    def create(self, db, indicator):
        indicator.id = self._next_id
        self._next_id += 1
        self._indicators[indicator.id] = indicator
        return indicator

    def update(self, db, indicator, data):
        for field, value in data.items():
            setattr(indicator, field, value)
        return indicator

    def delete(self, db, indicator):
        del self._indicators[indicator.id]


class FakeCountryRepository:
    """Ίδιο fake που είχαμε στο test_country_service.py -- εδώ το
    χρειαζόμαστε επειδή το IndicatorService ελέγχει αν η χώρα υπάρχει."""

    def __init__(self):
        self._countries: dict[int, Country] = {}

    def get_by_id(self, db, country_id):
        return self._countries.get(country_id)


@pytest.fixture()
def fake_indicator_repo(monkeypatch):
    repo = FakeIndicatorRepository()
    monkeypatch.setattr(indicator_service, "indicator_repository", repo)
    return repo


@pytest.fixture()
def fake_country_repo(monkeypatch):
    repo = FakeCountryRepository()
    monkeypatch.setattr(indicator_service, "country_repository", repo)
    return repo


def seed_indicators(repo: FakeIndicatorRepository, *indicators: Indicator) -> None:
    for ind in indicators:
        repo._indicators[ind.id] = ind
        repo._next_id = max(repo._next_id, ind.id + 1)


def seed_countries(repo: FakeCountryRepository, *countries: Country) -> None:
    for c in countries:
        repo._countries[c.id] = c


def test_list_indicators_returns_all(fake_indicator_repo, fake_country_repo):
    seed_indicators(
        fake_indicator_repo,
        Indicator(id=1, country_id=1, category="ECONOMIC", indicator_type="GDP_growth", year=2013, value=2.6),
        Indicator(id=2, country_id=2, category="MILITARY", indicator_type="troop_presence", year=1999, value=5000),
    )

    result = indicator_service.list_indicators(db=None)

    assert len(result) == 2


def test_get_indicator_returns_match(fake_indicator_repo, fake_country_repo):
    seed_indicators(
        fake_indicator_repo,
        Indicator(id=1, country_id=1, category="ECONOMIC", indicator_type="GDP_growth", year=2013, value=2.6),
    )

    result = indicator_service.get_indicator(db=None, indicator_id=1)

    assert result.value == 2.6


def test_get_indicator_raises_when_missing(fake_indicator_repo, fake_country_repo):
    with pytest.raises(IndicatorNotFoundError):
        indicator_service.get_indicator(db=None, indicator_id=999)


def test_list_indicators_by_country_filters_correctly(fake_indicator_repo, fake_country_repo):
    seed_indicators(
        fake_indicator_repo,
        Indicator(id=1, country_id=1, category="ECONOMIC", indicator_type="GDP_growth", year=2013, value=2.6),
        Indicator(id=2, country_id=2, category="ECONOMIC", indicator_type="GDP_growth", year=2013, value=1.1),
    )

    result = indicator_service.list_indicators_by_country(db=None, country_id=1)

    assert len(result) == 1
    assert result[0].country_id == 1


def test_create_indicator_persists_new_entry(fake_indicator_repo, fake_country_repo):
    seed_countries(fake_country_repo, Country(id=1, name="Serbia"))
    data = IndicatorCreate(
        country_id=1, category="ECONOMIC", indicator_type="GDP_growth", year=2013, value=2.6,
        source="World Bank API (NY.GDP.MKTP.KD.ZG)",
    )

    created = indicator_service.create_indicator(db=None, data=data)

    assert created.id is not None
    assert created.country_id == 1


def test_create_indicator_defaults_to_unverified(fake_indicator_repo, fake_country_repo):
    # Business rule: κάθε νέο indicator μπαίνει is_verified=False εξ ορισμού
    # (soft source check αντί για hard whitelist -- βλ. σχόλιο στο
    # IndicatorCreate), ανεξάρτητα από το τι δηλώνει το `source`. Μόνο
    # ρητό PUT από ADMIN το γυρίζει σε True.
    seed_countries(fake_country_repo, Country(id=1, name="Serbia"))
    data = IndicatorCreate(
        country_id=1, category="ECONOMIC", indicator_type="GDP_growth", year=2013, value=2.6,
        source="World Bank API (NY.GDP.MKTP.KD.ZG)",
    )

    created = indicator_service.create_indicator(db=None, data=data)

    assert created.is_verified is False


def test_create_indicator_rejects_missing_country(fake_indicator_repo, fake_country_repo):
    # Δεν κάναμε seed καμία χώρα -- το country_id=1 δεν υπάρχει
    data = IndicatorCreate(
        country_id=1, category="ECONOMIC", indicator_type="GDP_growth", year=2013, value=2.6,
        source="World Bank API (NY.GDP.MKTP.KD.ZG)",
    )

    with pytest.raises(CountryForIndicatorNotFoundError):
        indicator_service.create_indicator(db=None, data=data)


def test_update_indicator_changes_fields(fake_indicator_repo, fake_country_repo):
    seed_indicators(
        fake_indicator_repo,
        Indicator(id=1, country_id=1, category="ECONOMIC", indicator_type="GDP_growth", year=2013, value=2.6),
    )

    updated = indicator_service.update_indicator(
        db=None, indicator_id=1, data=IndicatorUpdate(value=3.1)
    )

    assert updated.value == 3.1


def test_update_indicator_raises_when_missing(fake_indicator_repo, fake_country_repo):
    with pytest.raises(IndicatorNotFoundError):
        indicator_service.update_indicator(db=None, indicator_id=999, data=IndicatorUpdate(value=1.0))


def test_delete_indicator_removes_entry(fake_indicator_repo, fake_country_repo):
    seed_indicators(
        fake_indicator_repo,
        Indicator(id=1, country_id=1, category="ECONOMIC", indicator_type="GDP_growth", year=2013, value=2.6),
    )

    indicator_service.delete_indicator(db=None, indicator_id=1)

    assert fake_indicator_repo.get_by_id(None, 1) is None


def test_delete_indicator_raises_when_missing(fake_indicator_repo, fake_country_repo):
    with pytest.raises(IndicatorNotFoundError):
        indicator_service.delete_indicator(db=None, indicator_id=999)