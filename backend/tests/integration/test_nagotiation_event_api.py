def test_create_event_with_participants(client):
    serbia = client.post("/countries", json={"name": "Serbia"}).json()
    kosovo = client.post("/countries", json={"name": "Kosovo"}).json()

    response = client.post("/negotiation-events", json={
        "title": "Rambouillet Talks",
        "date": "1999-02-06",
        "zopa_size": "NARROW",
        "negotiation_type": "DISTRIBUTIVE",
        "economic_weight": 3,
        "military_weight": 5,
        "social_weight": 2,
        "participants": [
            {"country_id": serbia["id"], "role": "PARTY"},
            {"country_id": kosovo["id"], "role": "PARTY"},
        ],
    })

    assert response.status_code == 201
    body = response.json()
    assert len(body["participants"]) == 2
    assert body["participants"][0]["country_name"] in ("Serbia", "Kosovo")


def test_create_event_with_invalid_weights_returns_422(client):
    response = client.post("/negotiation-events", json={
        "title": "Test Event",
        "date": "2000-01-01",
        "economic_weight": 5,
        "military_weight": 5,
        "social_weight": 5,
    })

    assert response.status_code == 422


def test_create_event_with_unknown_participant_country_returns_404(client):
    response = client.post("/negotiation-events", json={
        "title": "Test Event",
        "date": "2000-01-01",
        "economic_weight": 4,
        "military_weight": 4,
        "social_weight": 2,
        "participants": [{"country_id": 999, "role": "PARTY"}],
    })

    assert response.status_code == 404


def test_get_missing_event_returns_404(client):
    response = client.get("/negotiation-events/999")

    assert response.status_code == 404