import pytest

from app.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate
from app.services import country as country_service
from app.services.country import CountryNotFoundError, DuplicateCountryNameError


class FakeCountryRepository:
    """In-memory αντικαταστάτης του app.repositories.country -- χωρίς πραγματική ΒΔ."""

    def __init__(self):
        self._countries: dict[int, Country] = {}
        self._next_id = 1

    def get_all(self, db):
        return list(self._countries.values())

    def get_by_id(self, db, country_id):
        return self._countries.get(country_id)

    def get_by_name(self, db, name):
        return next((c for c in self._countries.values() if c.name == name), None)

    def create(self, db, country):
        country.id = self._next_id
        self._next_id += 1
        self._countries[country.id] = country
        return country

    def update(self, db, country, data):
        for field, value in data.items():
            setattr(country, field, value)
        return country

    def delete(self, db, country):
        del self._countries[country.id]


@pytest.fixture()
def fake_repo(monkeypatch):
    repo = FakeCountryRepository()
    monkeypatch.setattr(country_service, "country_repository", repo)
    return repo


def seed(repo: FakeCountryRepository, *countries: Country) -> None:
    for country in countries:
        repo._countries[country.id] = country
        repo._next_id = max(repo._next_id, country.id + 1)


def test_list_countries_returns_all(fake_repo):
    seed(fake_repo, Country(id=1, name="Serbia"), Country(id=2, name="Kosovo"))

    result = country_service.list_countries(db=None)

    assert {c.name for c in result} == {"Serbia", "Kosovo"}


def test_get_country_returns_match(fake_repo):
    seed(fake_repo, Country(id=1, name="Serbia"))

    result = country_service.get_country(db=None, country_id=1)

    assert result.name == "Serbia"


def test_get_country_raises_when_missing(fake_repo):
    with pytest.raises(CountryNotFoundError):
        country_service.get_country(db=None, country_id=999)


def test_create_country_persists_new_entry(fake_repo):
    data = CountryCreate(name="Serbia")

    created = country_service.create_country(db=None, data=data)

    assert created.id is not None
    assert created.name == "Serbia"
    assert fake_repo.get_by_id(None, created.id) is created


def test_create_country_rejects_duplicate_name(fake_repo):
    seed(fake_repo, Country(id=1, name="Serbia"))

    with pytest.raises(DuplicateCountryNameError):
        country_service.create_country(db=None, data=CountryCreate(name="Serbia"))


def test_update_country_changes_fields(fake_repo):
    seed(fake_repo, Country(id=1, name="Serbia", recognized_kosovo=False))

    updated = country_service.update_country(
        db=None, country_id=1, data=CountryUpdate(recognized_kosovo=True)
    )

    assert updated.recognized_kosovo is True


def test_update_country_raises_when_missing(fake_repo):
    with pytest.raises(CountryNotFoundError):
        country_service.update_country(db=None, country_id=999, data=CountryUpdate(name="X"))


def test_update_country_rejects_rename_to_existing_name(fake_repo):
    seed(fake_repo, Country(id=1, name="Serbia"), Country(id=2, name="Kosovo"))

    with pytest.raises(DuplicateCountryNameError):
        country_service.update_country(db=None, country_id=2, data=CountryUpdate(name="Serbia"))


def test_update_country_allows_keeping_same_name(fake_repo):
    seed(fake_repo, Country(id=1, name="Serbia"))

    updated = country_service.update_country(
        db=None, country_id=1, data=CountryUpdate(name="Serbia", country_code="SRB")
    )

    assert updated.country_code == "SRB"


def test_delete_country_removes_entry(fake_repo):
    seed(fake_repo, Country(id=1, name="Serbia"))

    country_service.delete_country(db=None, country_id=1)

    assert fake_repo.get_by_id(None, 1) is None


def test_delete_country_raises_when_missing(fake_repo):
    with pytest.raises(CountryNotFoundError):
        country_service.delete_country(db=None, country_id=999)
