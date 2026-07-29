def test_create_and_get_indicator(client):
    # Πρώτα φτιάχνουμε μια πραγματική χώρα μέσω του API (integration test
    # σημαίνει: όλα περνάνε από πραγματικά HTTP requests, όχι fakes)
    country_response = client.post("/countries", json={"name": "Serbia"})
    country_id = country_response.json()["id"]

    create_response = client.post("/indicators", json={
        "country_id": country_id,
        "category": "ECONOMIC",
        "indicator_type": "GDP_growth",
        "year": 2013,
        "value": 2.6,
    })
    assert create_response.status_code == 201
    indicator_id = create_response.json()["id"]

    get_response = client.get(f"/indicators/{indicator_id}")
    assert get_response.status_code == 200
    assert get_response.json()["value"] == 2.6


def test_create_indicator_with_missing_country_returns_404(client):
    response = client.post("/indicators", json={
        "country_id": 999,
        "category": "ECONOMIC",
        "indicator_type": "GDP_growth",
        "year": 2013,
        "value": 2.6,
    })

    assert response.status_code == 404


def test_list_indicators_by_country(client):
    serbia = client.post("/countries", json={"name": "Serbia"}).json()
    kosovo = client.post("/countries", json={"name": "Kosovo"}).json()

    client.post("/indicators", json={
        "country_id": serbia["id"], "category": "ECONOMIC",
        "indicator_type": "GDP_growth", "year": 2013, "value": 2.6,
    })
    client.post("/indicators", json={
        "country_id": kosovo["id"], "category": "ECONOMIC",
        "indicator_type": "GDP_growth", "year": 2013, "value": 1.1,
    })

    response = client.get(f"/indicators/by-country/{serbia['id']}")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_missing_indicator_returns_404(client):
    response = client.get("/indicators/999")

    assert response.status_code == 404