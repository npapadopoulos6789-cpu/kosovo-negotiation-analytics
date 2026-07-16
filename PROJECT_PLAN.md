# PROJECT_PLAN.md — Kosovo Negotiation Analytics

Agent-facing χρονοδιάγραμμα/roadmap. Για το domain model, τους κανόνες και τις
συμβάσεις δες [CLAUDE.md](CLAUDE.md) — αυτό εδώ είναι μόνο "πού είμαστε / τι ακολουθεί".

**Ενημερώθηκε:** 2026-07-17 · **Branch:** `main` · **Τελευταία αλλαγή:**
ολοκληρώθηκε το Country vertical slice (repository/service/schema/router/tests)

---

## Status snapshot

Το Country slice έκλεισε πλήρως — είναι πλέον το πρότυπο pattern για τα επόμενα.

| Κομμάτι | Κατάσταση |
|---|---|
| FastAPI app (skeleton, `GET /` health) | ✅ |
| DB connection (`Base`, `get_db()`) | ✅ |
| PostgreSQL via Docker Compose | ✅ |
| Alembic init + 1η migration (`countries` table) | ✅ |
| **`Country` slice (model/repo/service/schema/router/tests)** | ✅ **ολοκληρώθηκε** |
| `requirements.txt` + `pytest.ini` (δεν υπήρχαν καθόλου, προστέθηκαν) | ✅ |
| Indicator, NegotiationEvent, NegotiationAnalysis, User (models) | ❌ |
| Business rules (weights sum, Power Index, Power Gap, Window Score, Optimal Periods) | ❌ |
| LLM integration (`/synthesis`, ανά-event analysis) | ❌ |
| Auth (JWT, ρόλοι ADMIN/VIEWER) | ❌ — write endpoints του `/countries` είναι προς το παρόν ανοιχτά, θα γίνουν ADMIN-only στο slice 2 |
| Seed script (δεδομένα διπλωματικής) | ❌ |
| Tests (unit/integration) | ✅ 19 tests (11 unit + 8 integration) για το Country slice · 0 για τα υπόλοιπα |
| Frontend (React dashboard) | ❌ — δεν υπάρχει καν ο φάκελος |

**Σημείωση υποδομής:** δεν υπήρχε κανένα εγκατεστημένο Python περιβάλλον (ούτε
`requirements.txt`) όταν ξεκίνησε αυτό το slice. Εγκαταστάθηκαν
fastapi/uvicorn/sqlalchemy/psycopg2-binary/python-dotenv/alembic/pytest/httpx σε
Python 3.14 και καταγράφηκαν στο νέο `backend/requirements.txt`. Τα integration
tests τρέχουν με SQLite in-memory (όχι το πραγματικό Postgres — δεν ήταν
διαθέσιμο docker σε αυτό το session), οπότε δεν έχουν επιβεβαιωθεί έναντι
πραγματικού Postgres ακόμα.

## ✅ Αποφασισμένα (πρώην ασυνέπειες, ενημερώθηκε το CLAUDE.md)

1. **Entrypoint θέση.** Μένει στο `backend/main.py` (όχι `app/main.py`). Τρέχει με
   `uvicorn main:app` μέσα από το `backend/`. Routers θα κάνουν include σε αυτό
   το app instance.
2. **SQLAlchemy style.** Μένει classic style (`Column(...)`), όπως το υπάρχον
   `Country` model — ΟΧΙ 2.0 `Mapped[]`/`mapped_column`. Όλα τα επόμενα models
   ακολουθούν το ίδιο pattern.

## Roadmap — vertical slices με τη σειρά

Κάθε slice: model → migration (autogenerate + review) → repository → service →
schema (Pydantic v2) → router → unit tests (service) → integration tests (router).
Δεν ξεκινάει το επόμενο slice πριν κλείσει το προηγούμενο.

### 1. Country ✅ ΟΛΟΚΛΗΡΩΘΗΚΕ
Model + migration + repository (CRUD) + service (custom exceptions
`CountryNotFoundError`, `DuplicateCountryNameError`) + schema (Pydantic v2:
`CountryCreate`/`CountryUpdate`/`CountryRead`) + router (`/countries`, full
CRUD) + 19 tests (11 unit με mocked repository, 8 integration με TestClient).
Domain exceptions → HTTP status μέσω `@app.exception_handler` στο `main.py`
(404/409), όχι try/except στο router. Write endpoints είναι **προς το παρόν
ανοιχτά χωρίς auth** — το ADMIN-only gating μπαίνει στο slice 2 μαζί με τα
`get_current_user`/`require_admin` dependencies. **Αυτό είναι το πρότυπο
pattern για όλα τα επόμενα slices.**

### 2. User + Auth
`User` model (email, hashed_password, role) → JWT login/register →
`get_current_user` / `require_admin` dependencies. Χρειάζεται πριν μπουν
role-gated endpoints (Indicator verify, NegotiationEvent write).

### 3. Indicator
Model (country_id FK, category enum, indicator_type, year, value, unit, source,
is_verified) → CRUD slice → endpoint verify (ADMIN-only, `is_verified` toggle).

### 4. Power Index / Power Gap / Window Score / Optimal Periods (service layer)
Καθαρά ντετερμινιστικός υπολογιστικός πυρήνας πάνω σε Indicators — ΟΧΙ LLM,
ΟΧΙ νέο entity/table. Weights: Economic 40% / Military 40% / Social 20%.
Πρώτα unit tests με γνωστά inputs/outputs + edge cases (λείπουν indicators,
ένα μόνο έτος, μηδενικές τιμές), μετά endpoint(s) που τα εκθέτουν.

### 5. NegotiationEvent (+ event_participants)
Model με τα ZOPA/ripeness/BATNA/red lines πεδία + association table
(event_id, country_id, role) διαχειρίζεται μέσα από το event schema, όχι
ξεχωριστό endpoint. Business rule στο service:
`economic_weight + military_weight + social_weight == 10` → 422 αν παραβιάζεται.

### 6. NegotiationAnalysis + LLM integration
Model (nullable `negotiation_event_id`, `is_synthesis`) → LLM service
(`temperature=0`, JSON response, context = μόνο δομημένα πεδία event +
Indicators ±1-2 έτη + Power Index/Gap/Window Score/Optimal Periods +
participants) → `POST /events/{id}/analysis` και `POST /synthesis`.

### 7. Seed script
`python -m app.scripts.seed` — δεδομένα διπλωματικής, `is_verified=true`.
Μπαίνει μόλις υπάρχουν Country + Indicator + NegotiationEvent slices, ώστε να
γίνεται end-to-end δοκιμή με πραγματικά δεδομένα πριν το frontend.

### 8. Frontend (React dashboard)
Ξεκινάει αφού το API έχει τουλάχιστον Country + Indicator + NegotiationEvent +
Power Index endpoints σταθερά, ώστε να μη χρειάζεται ανασχεδιασμός contracts.

---

## Definition of done ανά slice

- [ ] Model σε `app/models/`, migration autogenerated **και ελεγμένη χειροκίνητα**
- [ ] Repository: μόνο CRUD queries, καμία λογική
- [ ] Service: business rules / custom exceptions εδώ, όχι στο router
- [ ] Schema: Pydantic v2, ποτέ SQLAlchemy model στο response
- [ ] Router: μόνο validation/DI/status codes
- [ ] Unit test(s) για κάθε service function
- [ ] Integration test(s) για κάθε endpoint
- [ ] `pytest -x -q` πράσινο πριν το commit
