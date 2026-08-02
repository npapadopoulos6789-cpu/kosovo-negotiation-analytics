import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_client(client):
    # Το "client" param δεν χρησιμοποιείται απευθείας εδώ, αλλά η εξάρτηση
    # είναι σκόπιμη: εγγυάται ότι το app.dependency_overrides[get_db] έχει
    # ήδη ρυθμιστεί στο ίδιο db_session πριν φτιάξουμε το δικό μας TestClient.
    with TestClient(app) as admin:
        admin.post("/auth/register", json={
            "email": "admin@test.com",
            "password": "secret123",
            "role": "ADMIN",
        })
        login_response = admin.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "secret123",
        })
        token = login_response.json()["access_token"]
        admin.headers.update({"Authorization": f"Bearer {token}"})
        yield admin
