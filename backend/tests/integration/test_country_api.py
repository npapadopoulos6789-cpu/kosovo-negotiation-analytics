def test_create_and_get_country(client, admin_client):
    create_response = admin_client.post("/countries", json={"name": "Serbia", "actor_type": "STATE"})
    assert create_response.status_code == 201
    country_id = create_response.json()["id"]

    get_response = client.get(f"/countries/{country_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Serbia"


def test_list_countries_returns_created_entries(client, admin_client):
    admin_client.post("/countries", json={"name": "Serbia"})
    admin_client.post("/countries", json={"name": "Kosovo"})

    response = client.get("/countries")

    assert response.status_code == 200
    names = {c["name"] for c in response.json()}
    assert names == {"Serbia", "Kosovo"}


def test_get_missing_country_returns_404(client):
    response = client.get("/countries/999")

    assert response.status_code == 404


def test_create_duplicate_name_returns_409(admin_client):
    admin_client.post("/countries", json={"name": "Serbia"})

    response = admin_client.post("/countries", json={"name": "Serbia"})

    assert response.status_code == 409


def test_create_country_missing_name_returns_422(admin_client):
    response = admin_client.post("/countries", json={})

    assert response.status_code == 422


def test_update_country(admin_client):
    create_response = admin_client.post("/countries", json={"name": "Serbia"})
    country_id = create_response.json()["id"]

    update_response = admin_client.put(
        f"/countries/{country_id}", json={"recognized_kosovo": False}
    )

    assert update_response.status_code == 200
    assert update_response.json()["recognized_kosovo"] is False


def test_update_missing_country_returns_404(admin_client):
    response = admin_client.put("/countries/999", json={"name": "X"})

    assert response.status_code == 404


def test_delete_country(client, admin_client):
    create_response = admin_client.post("/countries", json={"name": "Serbia"})
    country_id = create_response.json()["id"]

    delete_response = admin_client.delete(f"/countries/{country_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/countries/{country_id}")
    assert get_response.status_code == 404
