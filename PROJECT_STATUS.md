# Kosovo Negotiation Analytics — Κατάσταση Project

## Τι φτιάχνουμε (σύντομα)

FastAPI REST API + React dashboard που μετατρέπει τα ευρήματα της διπλωματικής μου
(διαπραγματεύσεις Σερβίας-Κοσόβου) σε ερευνήσιμη πλατφόρμα: πραγματικά δεδομένα +
ντετερμινιστικοί δείκτες ισχύος (Power Index/Gap/Window Score) + LLM-συνθετική
ανάλυση βάσει θεωριών διαπραγμάτευσης (Zartman ripeness, BATNA/ZOPA, red lines).
Coding Factory 10, ΟΠΑ — τελικό project.

**ΣΗΜΑΝΤΙΚΟ:** Μαθαίνω προγραμματισμό βήμα-βήμα. Εξήγησε πάντα ΓΙΑΤΙ πριν το ΤΙ,
μία εντολή/αλλαγή τη φορά, περίμενε επιβεβαίωση πριν προχωρήσεις στο επόμενο.

## Domain Model (5 entities)
Country (καλύπτει και διεθνείς δρώντες: actor_type, geopolitical_bloc,
recognized_kosovo, country_code) · Indicator (category ECONOMIC/MILITARY/
SOCIAL_UNREST, is_verified) · NegotiationEvent (zopa/ripeness/batna/red lines/
weights 4-4-2, event_participants) · NegotiationAnalysis (LLM Q&A + synthesis) ·
User (ADMIN/VIEWER)

## Αρχιτεκτονική
`api/` (routers, μόνο HTTP) → `services/` (business logic) → `repositories/`
(μόνο DB queries) → `models/` (SQLAlchemy). Ποτέ λογική σε routers/repositories.
Στοίβα: FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL (Docker) + React + JWT auth
+ pytest. Κανόνας δεδομένων: ground truth από τη διπλωματική (seed), υπολογισμοί
(Power Index κ.λπ.) από δικό μας κώδικα, LLM μόνο ερμηνεία πάνω σε δοθέντα.

## GitHub
https://github.com/npapadopoulos6789-cpu/kosovo-negotiation-analytics

---

## ΠΟΥ ΒΡΙΣΚΟΜΑΣΤΕ ΤΩΡΑ (ενημέρωσε αυτό το κομμάτι σε κάθε session)

**Έχουν ολοκληρωθεί:**
- venv, FastAPI "Hello World", πλήρης δομή φακέλων (models/schemas/repositories/
  services/api/core), όλα τα `__init__.py`
- PostgreSQL τρέχει σε Docker (`docker-compose.yml` στη ρίζα)
- `.env` με DATABASE_URL, `app/core/database.py` (engine, SessionLocal, Base, get_db)
- `app/models/country.py` (Country model με actor_type/geopolitical_bloc/
  recognized_kosovo/country_code, enums ActorType/GeopoliticalBloc)
- Alembic: `alembic init`, `env.py` ρυθμισμένο (διαβάζει .env, target_metadata =
  Base.metadata), πρώτο migration `27011cfbfeba_create_countries_table.py`
  δημιουργήθηκε ΚΑΙ εφαρμόστηκε (`alembic upgrade head`) — ο πίνακας `countries`
  υπάρχει πραγματικά στη ΒΔ
- Git/GitHub: repo συνδεδεμένο
- **Country vertical slice — ΟΛΟΚΛΗΡΟ, committed (`211ee88`):**
  `app/repositories/country.py`, `app/services/country.py` (custom domain
  exceptions `CountryNotFoundError`/`DuplicateCountryNameError`),
  `app/schemas/country.py`, `app/api/country.py` — πλήρες CRUD
  (GET list, GET by id, POST, PUT, DELETE). Entrypoint είναι `backend/main.py`
  (ΟΧΙ `app/main.py`) — εκεί γίνεται `include_router` + exception handlers
  που κάνουν map τα custom exceptions σε 404/409.
- 19 unit/integration tests στο `backend/tests/` (`pytest.ini`,
  `requirements.txt` προστέθηκαν στο ίδιο commit)

**Σημείωση για προηγούμενη σύγχυση:** είχαν δημιουργηθεί χειροκίνητα 4 duplicate
αρχεία (`country_router.py`, `country_repository.py`, `country_schema.py`,
`country_service.py`, class-based στυλ) πριν γίνει σαφές ότι το slice ήταν ήδη
πλήρες και committed. Διαγράφηκαν στις 2026-07-29 — δεν ήταν συνδεδεμένα
πουθενά, το `backend/main.py` έκανε πάντα import από τα `country.py` αρχεία.

- **Indicator vertical slice — ΟΛΟΚΛΗΡΟ, ΔΕΝ έχει γίνει commit ακόμα:**
  `app/models/indicator.py` (FK σε `countries.id`, enum `IndicatorCategory`),
  `app/repositories/indicator.py`, `app/services/indicator.py` (custom
  exceptions `IndicatorNotFoundError`/`CountryForIndicatorNotFoundError`,
  business rule: η χώρα του indicator πρέπει να υπάρχει), `app/schemas/indicator.py`
  (Base/Create/Update/Read στυλ), `app/api/indicator.py` — πλήρες CRUD +
  extra endpoint `GET /indicators/by-country/{country_id}`. Ίδιο pattern με
  το Country ακριβώς. Migration `51bb723cd8d8_create_indicators_table.py`
  γράφτηκε ΚΑΙ εφαρμόστηκε (`alembic current` → head), `alembic/env.py`
  ενημερώθηκε με το import του `Indicator` model. Router συνδέθηκε στο
  `backend/main.py` + exception handlers για τα δύο custom exceptions.
  Tests: `tests/unit/test_indicator_service.py` (10 tests, fake repos) +
  `tests/integration/test_indicator_api.py` (4 tests, πραγματικό HTTP μέσω
  TestClient). Σύνολο `pytest -q` στο `backend/`: **34 passed** (19 Country +
  15 Indicator).
- Στην πορεία υπήρξε ενδιάμεση σύγχυση: το πρώτο draft του `app/api/indicator.py`
  ήταν σε παλιό class-based στυλ (`IndicatorService`, `IndicatorResponse`) που
  δεν ταίριαζε με το function-based `services/indicator.py` — διορθώθηκε στο
  ίδιο session, τώρα ταιριάζει 100% με το Country router pattern.

**Επόμενο βήμα:**
1. Commit του Indicator slice (μοντέλο/repo/service/schema/router/migration/tests)
   + του καθαρισμού των Country duplicates — είναι ακόμα uncommitted μαζί
2. Push στο GitHub
3. Μετά: συνέχεια στο NegotiationEvent entity (ίδιο pattern, αλλά προσοχή στο
   business rule weights sum=10 και στο association table `event_participants`)

**Σημειώσεις/μαθήματα από προβλήματα που ξανασυναντήσαμε:**
- Αρχεία (π.χ. country.py, .env) έχουν "χαθεί" 2-3 φορές — να ελέγχεται πάντα
  ότι υπάρχουν πριν συνεχίσουμε
- Πριν ξεκινήσουμε νέο slice χειροκίνητα, να ελέγχουμε πρώτα `git log` / `git
  status` μήπως υπάρχει ήδη committed δουλειά — απέφυγε ξανά τη σύγχυση duplicate
  αρχείων που έγινε με το Country slice
- Προσοχή PowerShell vs cmd (πρέπει να βλέπουμε `PS` στο prompt)
- Να ενεργοποιείται το venv σε κάθε νέο terminal (`venv\Scripts\Activate.ps1`)
- GitHub account που χρησιμοποιούμε: npapadopoulos6789-cpu (όχι pouritanos42)
