import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.services import user as user_service
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
def admin_client(client, db_session):
    # POST /auth/register δεν μπορεί ΠΙΑ να φτιάξει ADMIN (security fix --
    # το role αγνοείται πάντα εκεί, βλ. services/user.py
    # register_public_user). Το test-admin εδώ φτιάχνεται απευθείας μέσω
    # του internal register_user (ίδιο service που χρησιμοποιεί και το
    # seed script για τον πραγματικό ADMIN_EMAIL/ADMIN_PASSWORD admin) --
    # ΟΧΙ μέσω HTTP register. Το "client" param εξακολουθεί να χρειάζεται
    # ρητά: εγγυάται ότι το app.dependency_overrides[get_db] έχει ήδη
    # ρυθμιστεί στο ίδιο db_session πριν το login POST παρακάτω.
    user_service.register_user(
        db_session,
        UserCreate(email="admin@test.com", password="secret123", role=UserRole.ADMIN),
    )
    with TestClient(app) as admin:
        login_response = admin.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "secret123",
        })
        token = login_response.json()["access_token"]
        admin.headers.update({"Authorization": f"Bearer {token}"})
        yield admin


@pytest.fixture()
def viewer_client(client):
    # Απλός συνδεδεμένος χρήστης (VIEWER, ΟΧΙ ADMIN) -- μέσω του
    # πραγματικού public POST /auth/register, που τώρα φτιάχνει ΠΑΝΤΑ
    # VIEWER (βλ. admin_client παραπάνω για το γιατί το ADMIN δεν μπορεί
    # πια να φτιαχτεί μέσω αυτού του endpoint). Χρησιμοποιείται εκεί που
    # ένα endpoint απαιτεί ΟΠΟΙΟΝΔΗΠΟΤΕ συνδεδεμένο χρήστη (π.χ.
    # /synthesis, /compare), όχι συγκεκριμένα ADMIN.
    with TestClient(app) as viewer:
        viewer.post("/auth/register", json={
            "email": "viewer@test.com",
            "password": "secret123",
        })
        login_response = viewer.post("/auth/login", json={
            "email": "viewer@test.com",
            "password": "secret123",
        })
        token = login_response.json()["access_token"]
        viewer.headers.update({"Authorization": f"Bearer {token}"})
        yield viewer
