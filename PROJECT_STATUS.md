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

_Τελευταία πλήρης ανανέωση: 2026-08-02. `git status` καθαρό, όλα committed_
_και pushed. `pytest -q` στο `backend/`: **51 passed**, 0 failed._

### Infrastructure
- venv, πλήρης δομή φακέλων (`models/schemas/repositories/services/api/core`)
- PostgreSQL σε Docker (`docker-compose.yml` στη ρίζα), `.env` με DATABASE_URL
- `app/core/database.py` (engine, SessionLocal, Base, get_db)
- Alembic ρυθμισμένο (`env.py` διαβάζει `.env`, `target_metadata = Base.metadata`).
  5 migrations, όλα εφαρμοσμένα στη ΒΔ (`alembic current` → head):
  `countries` → `indicators` → `users` → `negotiation_events` +
  `event_participants` → `negotiation_analyses`
- Entrypoint: **`backend/main.py`** (ΟΧΙ `app/main.py`) — εκεί γίνονται όλα τα
  `include_router(...)` + exception handlers που κάνουν map custom domain
  exceptions σε HTTP status codes (404/409/422/401)
- Git/GitHub: repo συνδεδεμένο, https://github.com/npapadopoulos6789-cpu/kosovo-negotiation-analytics,
  ενημερωμένο μέχρι το commit `cee82a1`

### Τα 5 entities — όλα ολοκληρωμένα ως vertical slices (model → migration →
### repository → service → schema → router → tests), ίδιο pattern παντού:
### function-based repository/service, custom domain exceptions, Pydantic
### Base/Create/Update/Read schemas

1. **Country** — πλήρες CRUD. Business rule: όχι διπλότυπο όνομα
   (`DuplicateCountryNameError` → 409).
2. **Indicator** — πλήρες CRUD + `GET /indicators/by-country/{country_id}`.
   Business rule: η χώρα πρέπει να υπάρχει (`CountryForIndicatorNotFoundError`).
3. **NegotiationEvent** — πλήρες CRUD, με nested `participants` (association
   table `event_participants`, roles PARTY/MEDIATOR/GUARANTOR). Business rules:
   βάρη economic/military/social πρέπει να αθροίζουν σε 10
   (`InvalidWeightsError` → 422, ελέγχεται σωστά και σε partial update), κάθε
   participant country πρέπει να υπάρχει (`CountryForParticipantNotFoundError`).
   Το `ParticipantRead.country_name` καλύπτεται από `@property` στο
   `EventParticipant` model (`return self.country.name`) — δεν χρειάστηκε
   καμία επιπλέον λογική σε service/schema.
4. **NegotiationAnalysis** — CRUD μόνο GET+POST (χωρίς PUT/DELETE, δεν βγάζει
   νόημα να επεξεργαστείς μια LLM απάντηση). Business rule:
   `negotiation_event_id=None` → `is_synthesis=True` αυτόματα· αν δοθεί
   event_id, πρέπει να υπάρχει (`EventForAnalysisNotFoundError`).
   **ΠΡΟΣΩΡΙΝΑ δεν καλεί ακόμα το LLM** — το `POST /negotiation-analyses`
   αποθηκεύει μόνο το `user_question`, με `llm_answer=None`,
   `model_used=None`. Το πραγματικό OpenAI integration (system prompt με
   strict context, temperature=0) είναι το επόμενο ξεχωριστό βήμα.
5. **User + Auth** — `app/models/user.py` (email, hashed_password, role
   ADMIN/VIEWER), `app/core/security.py` (password hashing, JWT create/decode),
   `POST /auth/register`, `POST /auth/login` (JSON body, όχι OAuth2 form —
   επιστρέφει `{access_token, token_type}`).

### Authorization — ενεργό σε όλα τα entities
`app/core/dependencies.py`: `get_current_user` (decode JWT από
`Authorization: Bearer <token>`) και `require_admin` (401 αν δεν υπάρχει
έγκυρο token, 403 αν ο χρήστης δεν είναι ADMIN). Εφαρμόζεται ως
`Depends(require_admin)` σε **όλα** τα POST/PUT/DELETE των Country/Indicator/
NegotiationEvent (`create_analysis` του NegotiationAnalysis είναι ΣΚΟΠΙΜΑ
χωρίς `require_admin` — οποιοσδήποτε συνδεδεμένος χρήστης, ADMIN ή VIEWER,
επιτρέπεται να ζητήσει LLM ανάλυση, μόνο η διαχείριση δεδομένων είναι
ADMIN-only). Όλα τα GET endpoints παραμένουν δημόσια, χωρίς authentication.
Επιβεβαιώθηκε end-to-end με live curl requests (register/login/POST με και
χωρίς token → 200/201/401 όπως αναμενόταν).

### Tests
`backend/tests/`: 4 unit test files (fake repositories, χωρίς πραγματική ΒΔ)
+ 3 integration test files (πραγματικά HTTP requests μέσω `TestClient` σε
SQLite in-memory). Fixtures στο `conftest.py`: `client` (χωρίς auth, για GET-only
tests) και `admin_client` (κάνει register+login ADMIN αυτόματα, βάζει
`Authorization` header — χρησιμοποιείται σε όλα τα write tests). Σύνολο:
**51 passed**.

**Επόμενο βήμα:**
1. Πραγματικό LLM integration στο `NegotiationAnalysis.create_analysis`
   (OpenAI API call, strict prompt μόνο πάνω σε δοθέν context, temperature=0,
   άρνηση αν λείπουν δεδομένα — βλ. κανόνες LLM integration στο CLAUDE.md)
2. Ντετερμινιστικοί υπολογισμοί: Power Index / Power Gap / Window Score /
   Optimal Periods (service layer, ΟΧΙ LLM, βλ. business rules στο CLAUDE.md)
3. `POST /synthesis` endpoint (context = όλα τα events + scores, `is_synthesis=true`)
4. Seed script με τα πραγματικά δεδομένα της διπλωματικής (`is_verified=true`)
5. Μετά: React frontend (`frontend/`, δεν έχει ξεκινήσει ακόμα)

**Σημειώσεις/μαθήματα από προβλήματα που ξανασυναντήσαμε:**
- Αρχεία (π.χ. country.py, .env) έχουν "χαθεί" 2-3 φορές — να ελέγχεται πάντα
  ότι υπάρχουν πριν συνεχίσουμε
- Πριν ξεκινήσουμε νέο slice χειροκίνητα, να ελέγχουμε πρώτα `git log` / `git
  status` μήπως υπάρχει ήδη committed δουλειά — απέφυγε ξανά τη σύγχυση duplicate
  αρχείων που έγινε με το Country slice
- `POST /auth/login` θέλει JSON body (`UserLogin` schema), όχι OAuth2
  form-data, παρόλο που χρησιμοποιείται `OAuth2PasswordBearer` για το Swagger UI
- Προσοχή PowerShell vs cmd (πρέπει να βλέπουμε `PS` στο prompt)
- Να ενεργοποιείται το venv σε κάθε νέο terminal (`venv\Scripts\Activate.ps1`)
- GitHub account που χρησιμοποιούμε: npapadopoulos6789-cpu (όχι pouritanos42)
