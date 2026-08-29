def test_register_creates_viewer_by_default(client):
    response = client.post("/auth/register", json={
        "email": "newuser@test.com",
        "password": "secret123",
    })

    assert response.status_code == 201
    assert response.json()["role"] == "VIEWER"


def test_register_ignores_client_supplied_admin_role(client):
    # ΚΡΙΣΙΜΟ security test: πριν το fix, ένα "role": "ADMIN" στο request
    # body δημιουργούσε πραγματικό ADMIN λογαριασμό μέσω του public
    # register endpoint -- κανένα auth/authorization δεν χρειαζόταν.
    # UserRegister (το request schema, βλ. schemas/user.py) δεν έχει καν
    # πεδίο role, άρα αυτό το "role" αγνοείται σιωπηλά -- ο χρήστης
    # ΠΡΕΠΕΙ να βγει VIEWER, ό,τι κι αν έστειλε ο client.
    response = client.post("/auth/register", json={
        "email": "wannabe-admin@test.com",
        "password": "secret123",
        "role": "ADMIN",
    })

    assert response.status_code == 201
    assert response.json()["role"] == "VIEWER"


def test_register_duplicate_email_returns_409(client):
    client.post("/auth/register", json={"email": "dup@test.com", "password": "secret123"})

    response = client.post("/auth/register", json={"email": "dup@test.com", "password": "secret123"})

    assert response.status_code == 409


def test_register_then_login_succeeds(client):
    client.post("/auth/register", json={"email": "login@test.com", "password": "secret123"})

    response = client.post("/auth/login", json={"email": "login@test.com", "password": "secret123"})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_returns_401(client):
    client.post("/auth/register", json={"email": "wrongpass@test.com", "password": "secret123"})

    response = client.post("/auth/login", json={"email": "wrongpass@test.com", "password": "nope"})

    assert response.status_code == 401
