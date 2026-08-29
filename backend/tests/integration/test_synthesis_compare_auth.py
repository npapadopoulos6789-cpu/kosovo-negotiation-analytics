# POST /synthesis και POST /compare απαιτούν ΟΠΟΙΟΝΔΗΠΟΤΕ συνδεδεμένο
# χρήστη (VIEWER ή ADMIN) -- ΟΧΙ require_admin, ΟΧΙ δημόσια πρόσβαση.
# Το per-event Q&A (POST /negotiation-analyses/) ΔΕΝ αλλάζει, μένει
# δημόσιο -- δεν το αγγίζουμε εδώ.

from app.services import negotiation_analysis as analysis_service

FAKE_LLM_RAW_TEXT = '{"answer": "fake", "answer_certainty": "HIGH", "data_gaps_noted": []}'


def _mock_llm(monkeypatch):
    # Ίδιο μοτίβο με tests/unit/test_negotiation_analysis_service.py --
    # ΚΑΝΕΝΑ πραγματικό Anthropic API call μέσα από pytest.
    def fake_call(system_prompt, user_message, max_tokens=8192):
        return {"raw_text": FAKE_LLM_RAW_TEXT, "model": "fake-model"}

    monkeypatch.setattr(analysis_service.llm_client, "call_llm", fake_call)


def test_synthesis_requires_login(client):
    response = client.post("/synthesis", json={"user_question": "test?"})

    assert response.status_code == 401


def test_compare_requires_login(client):
    response = client.post("/compare", json={"event_a_id": 1, "event_b_id": 2})

    assert response.status_code == 401


def test_synthesis_succeeds_for_plain_viewer(admin_client, viewer_client, monkeypatch):
    # VIEWER, ΟΧΙ ADMIN -- επιβεβαιώνει ρητά ότι require_admin ΔΕΝ
    # χρησιμοποιείται εδώ, μόνο get_current_user.
    _mock_llm(monkeypatch)

    # Το synthesis context χρειάζεται Serbia/Kosovo (calculate_power_index
    # κ.λπ., βλ. negotiation_analysis.py _build_synthesis_context) --
    # χωρίς αυτά σκάει με AttributeError πριν καν φτάσει στο LLM mock.
    admin_client.post("/countries", json={"name": "Serbia"})
    admin_client.post("/countries", json={"name": "Kosovo"})

    response = viewer_client.post("/synthesis", json={"user_question": "test?"})

    assert response.status_code == 201


def test_compare_succeeds_for_plain_viewer(admin_client, viewer_client, monkeypatch):
    _mock_llm(monkeypatch)

    # Τα events χρειάζονται ADMIN για να δημιουργηθούν (ξεχωριστός κανόνας
    # από το ποιος μπορεί να ζητήσει compare) -- ο viewer_client κάνει
    # μόνο το ίδιο το compare call.
    serbia = admin_client.post("/countries", json={"name": "Serbia"}).json()
    kosovo = admin_client.post("/countries", json={"name": "Kosovo"}).json()
    event_a = admin_client.post("/negotiation-events", json={
        "title": "Rambouillet Talks",
        "date": "1999-02-06",
        "economic_weight": 3,
        "military_weight": 5,
        "social_weight": 2,
        "participants": [{"country_id": serbia["id"], "role": "PARTY"}],
    }).json()
    event_b = admin_client.post("/negotiation-events", json={
        "title": "Brussels Agreement",
        "date": "2013-04-19",
        "economic_weight": 4,
        "military_weight": 4,
        "social_weight": 2,
        "participants": [{"country_id": kosovo["id"], "role": "PARTY"}],
    }).json()

    response = viewer_client.post(
        "/compare", json={"event_a_id": event_a["id"], "event_b_id": event_b["id"]}
    )

    assert response.status_code == 201
