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

_Τελευταία πλήρης ανανέωση: 2026-08-02, μετά το SEED_DATA_SPEC.md Στάδιο 1+2._
_`pytest -q` στο `backend/`: **73 passed**, 0 failed._
_⚠️ `git status` ΔΕΝ είναι καθαρό — 10 τροποποιημένα αρχεία + 1 νέο migration_
_ακόμα uncommitted (τελευταίο commit: `16be597`). Βλ. λίστα στο τέλος αυτού_
_του section._

### Infrastructure
- venv, πλήρης δομή φακέλων (`models/schemas/repositories/services/api/core`)
- PostgreSQL σε Docker (`docker-compose.yml` στη ρίζα), `.env` με DATABASE_URL
- `app/core/database.py` (engine, SessionLocal, Base, get_db)
- Alembic ρυθμισμένο (`env.py` διαβάζει `.env`, `target_metadata = Base.metadata`).
  **6 migrations**, όλα εφαρμοσμένα σε φρέσκια ΒΔ (`alembic current` → head
  `b536861761e3`): `countries` → `indicators` → `negotiation_events` +
  `event_participants` → `users` → `negotiation_analyses` →
  `confidence`(Indicator) + `implementation_success`(NegotiationEvent)
- Entrypoint: **`backend/main.py`** (ΟΧΙ `app/main.py`) — εκεί γίνονται όλα τα
  `include_router(...)` + exception handlers που κάνουν map custom domain
  exceptions σε HTTP status codes (404/409/422/401)
- Git/GitHub: repo συνδεδεμένο, https://github.com/npapadopoulos6789-cpu/kosovo-negotiation-analytics,
  τελευταίο commit `16be597` (οι σημερινές αλλαγές δεν έχουν γίνει commit ακόμα)
- `requirements.txt` διορθώθηκε 2026-08-02: έλειπαν `bcrypt`, `python-jose[cryptography]`,
  `email-validator` — όλα ήδη χρησιμοποιούνταν από το `core/security.py`/Pydantic
  `EmailStr` αλλά δεν ήταν καταγεγραμμένα· fresh install θα έσκαγε

### Τα 5 entities — όλα ολοκληρωμένα ως vertical slices (model → migration →
### repository → service → schema → router → tests), ίδιο pattern παντού:
### function-based repository/service, custom domain exceptions, Pydantic
### Base/Create/Update/Read schemas

1. **Country** — πλήρες CRUD. Business rule: όχι διπλότυπο όνομα
   (`DuplicateCountryNameError` → 409).
2. **Indicator** — πλήρες CRUD + `GET /indicators/by-country/{country_id}`.
   Business rule: η χώρα πρέπει να υπάρχει (`CountryForIndicatorNotFoundError`).
   **Νέο πεδίο (2026-08-02): `confidence`** — enum `EXACT | CHART_READ | RANGE`,
   nullable, σε model/schema (Create/Update/Read). Migration `b536861761e3`.
3. **NegotiationEvent** — πλήρες CRUD, με nested `participants` (association
   table `event_participants`, roles PARTY/MEDIATOR/GUARANTOR). Business rules:
   βάρη economic/military/social πρέπει να αθροίζουν σε 10
   (`InvalidWeightsError` → 422, ελέγχεται σωστά και σε partial update), κάθε
   participant country πρέπει να υπάρχει (`CountryForParticipantNotFoundError`).
   Το `ParticipantRead.country_name` καλύπτεται από `@property` στο
   `EventParticipant` model (`return self.country.name`) — δεν χρειάστηκε
   καμία επιπλέον λογική σε service/schema.
   **Νέο πεδίο (2026-08-02): `implementation_success`** — Float 0.0-1.0,
   nullable, δεν επιβάλλεται εύρος στη ΒΔ (ίδιο μοτίβο με τα weights). Ίδιο migration.
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

### Analytics core (`app/services/analytics.py` + `app/api/analytics.py`) — ΟΛΟΚΛΗΡΟ
Καθαρά ντετερμινιστικός υπολογιστικός πυρήνας, ΧΩΡΙΣ LLM, ήδη συνδεδεμένο στο
`main.py` (`app.include_router(analytics_router)`). GET-only, δημόσιο (χωρίς
`require_admin` — είναι απλή ανάγνωση/υπολογισμός, όχι write στα δεδομένα):
- `normalize` / `get_category_score` / `calculate_power_index` (Economic 40% /
  Military 40% / Social 20%, όπως στο CLAUDE.md)
- `calculate_power_gap`, `calculate_trend_score`, `calculate_social_pressure_score`,
  `calculate_window_score` (50% συμμετρία + 30% τάση + 20% κοινωνική πίεση)
- `find_optimal_agreement_period`, `find_optimal_mutual_compromise_period`,
  `find_best_moments` (confidence HIGH/MEDIUM/LOW — βλ. CLAUDE.md για λεπτομέρειες)
- `NORMALIZATION_RANGES` καλύπτει και τους 6 `indicator_type` που όντως seed-άρονται
  (επιβεβαιώθηκε 2026-08-02, καμία αλλαγή δεν χρειάστηκε)
- 22 unit tests, όλα με mocked repositories/monkeypatch
- ⚠️ Ο router κάνει `raise HTTPException` απευθείας μέσα στα endpoints, αντί να
  αφήνει το service να πετάει custom exception που πιάνεται στο `main.py` — μόνο
  αυτός ο router αποκλίνει από το πρότυπο. Δεν το άγγιξα, θέλει απόφαση (βλ. Επόμενο βήμα).
- **`KEY_YEARS` επεκτάθηκε 2026-08-02**: `[1998, 1999, 2000, 2005, 2007, 2008,
  2013, 2018, 2020, 2023]` (ήταν `[1999, 2005, 2007, 2008, 2013, 2023]`) — τα
  4 νέα έτη (1998/2000/2018/2020) προστέθηκαν για τα validation tests P1-P5
  του `SEED_DATA_SPEC.md` §4.1 (βλ. Στάδιο 3 στο Επόμενο βήμα).
- ⚠️ **Εύρημα κάλυψης δεδομένων (2026-08-02, δεν επιλύθηκε ακόμα):** το
  `calculate_power_index` απαιτεί exact-year match ΚΑΙ στις 3 κατηγορίες.
  Με τα σημερινά indicators, πλήρες Power Index υπάρχει ΜΟΝΟ για: Serbia
  {2005, 2007, 2013, 2023}, Kosovo {2013, 2023} (το `GDP_growth` Κοσόβου
  καλύπτει μόνο αυτά τα δύο έτη — World Bank API δεν έχει Κόσοβο πριν το
  2009). Power Gap άρα υπολογίσιμο μόνο {2013, 2023}. Πρακτικά: το P1
  (Serbia collapse 1999) και μέρος του P2/P4 δεν μπορούν να δοκιμαστούν
  κυριολεκτικά με πραγματικά δεδομένα σήμερα — χρειάζεται απόφαση στο
  Στάδιο 3 (re-interpret το test ή αποδοχή `None` με τεκμηρίωση γιατί).

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

### Seed script (`app/scripts/seed.py`) — ενημερώθηκε 2026-08-02 βάσει SEED_DATA_SPEC.md
9 countries/actors, **51 indicators**, **10 negotiation events (E1-E10, πλήρες
σετ του spec)**. Ρητές αποφάσεις αυτής της αναθεώρησης (όχι τυφλή υιοθέτηση
του spec — βλ. λεπτομέρειες στο commit message όταν γίνει commit):
- Serbia `GDP_growth`/`unemployment_rate`: **παρέμειναν** οι live World Bank
  API τιμές (όχι του spec) — προστέθηκε `confidence=EXACT`
- Freedom House scores (Serbia+Kosovo, 10 σημεία/χώρα): **υιοθετήθηκαν** οι
  τιμές του spec §2.4, `confidence=CHART_READ` (αντικατέστησαν τις 5
  παλαιότερες τιμές/χώρα — **παρατήρηση:** το 2008 δεν υπάρχει πια σε καμία
  από τις δύο FH σειρές, το spec δεν το καλύπτει)
- Kosovo `trade_share_eu`: **υιοθετήθηκε** 44.7 (spec, μόνο εισαγωγές) αντί
  του παλιότερου δικού μας μέσου όρου εισαγωγών/εξαγωγών (35.8)
- Military (`military_expenditure_pct_gdp` Serbia, `troop_presence_index`
  Kosovo): **παρέμειναν αμετάβλητα** — τα boolean markers του spec
  (`unsc_veto_protection` κ.λπ.) **δεν** προστέθηκαν
- Kosovo `GDP_growth`: **παρέμεινε αμετάβλητο** (δεν υπάρχει αντίστοιχο στο spec)
- 4 events προστέθηκαν (E1 Autonomy Revocation 1989, E4 Standards Before
  Status 2003, E8 Tariffs 2018, E9 Washington Agreement 2020), το
  "UNMIK Interim Administration" **αφαιρέθηκε** (δεν ήταν στα E1-E10),
  weights/zopa/ripeness ενημερώθηκαν σε όλα τα κοινά events ώστε να
  ταιριάζουν ΑΚΡΙΒΩΣ με το spec. `implementation_success` γεμίστηκε στα 6
  events του πίνακα §4.4 (Rambouillet 0.0, Ψήφισμα 1244 0.7, Ahtisaari 0.0,
  Βρυξέλλες 0.3, Ουάσιγκτον 0.1, Οχρίδα 0.2), `None` στα υπόλοιπα 4
- Participants για τα νέα/E events **δεν δίνονται ρητά στο spec** — επιλέχθηκαν
  βάσει contextual actors στο batna κείμενο κάθε event (σχολιασμένο inline
  στο seed.py, π.χ. E4→UN mediator γιατί UNMIK διοικούσε την περίοδο)
- Ahtisaari (E5) `negotiation_type`: το spec δίνει διπλή ετικέτα
  ("INTEGRATIVE ως πρόθεση / DISTRIBUTIVE ως έκβαση") — επιλέχθηκε
  `DISTRIBUTIVE` (βάσει έκβασης/απόρριψης), judgment call
- **Ρητά ΔΕΝ προστέθηκαν ακόμα** (σχόλιο "Future Work" στο seed.py, βλ.
  `SEED_DATA_SPEC.md` §2.1-2.4): `eu_fdi_share`, `eu_preaccession_funds`,
  `russian_gas_dependency`, `chinese_loans_cumulative`, `trade_volume_*` ανά
  εταίρο, Kosovo `GDP_per_capita`, δημογραφικά, `has_own_currency`/
  `has_sovereign_bond_market`, `international_recognitions`, event-markers
  (`ethnic_violence_event` κ.λπ.)
- Επιβεβαιώθηκε με πλήρες reset ΒΔ (`docker compose down -v` → `up -d db` →
  `alembic upgrade head` → `python -m app.scripts.seed`) — 9/51/10 εγγραφές,
  `pytest -q` ανεπηρέαστο (73 passed, SQLite in-memory)
- 🐛 Διορθώθηκε στο πέρασμα: το τελικό `print("...✅...")` έσκαγε με
  `UnicodeEncodeError` σε Windows console με cp1253 codepage (αφαιρέθηκε το
  emoji, καθαρά cosmetic, καμία επίπτωση σε δεδομένα)

### Tests
`backend/tests/`: 5 unit test files (fake repositories/monkeypatch, χωρίς
πραγματική ΒΔ: country, indicator, negotiation_event, negotiation_analysis,
analytics) + 3 integration test files (πραγματικά HTTP requests μέσω
`TestClient` σε SQLite in-memory: country, indicator, negotiation_event).
Fixtures στο `conftest.py`: `client` (χωρίς auth, για GET-only tests) και
`admin_client` (κάνει register+login ADMIN αυτόματα, βάζει `Authorization`
header — χρησιμοποιείται σε όλα τα write tests). Σύνολο: **73 passed**.

**Κενά στο test coverage** (εντοπίστηκαν 2026-08-02, δεν διορθώθηκαν ακόμα):
- `User`/auth service (`register_user`, `authenticate_user`) δεν έχει δικό του
  unit test file — δοκιμάζεται μόνο έμμεσα μέσω του `admin_client` fixture
- Δεν υπάρχει integration test file για `negotiation-analyses` ή για
  `analytics` endpoints (μόνο unit tests με mocks)

**Επόμενο βήμα:**
1. **Commit** των σημερινών (2026-08-02) αλλαγών — βλ. λίστα uncommitted
   αρχείων στο τέλος αυτού του section, ΔΕΝ έχει γίνει ακόμα
2. **SEED_DATA_SPEC.md Στάδιο 3** (εγκεκριμένο ως επόμενο βήμα, όχι ακόμα
   ξεκινημένο): P1-P5 validation tests σε νέο `tests/unit/test_validation_targets.py`,
   integration-style πάνω στην ήδη γεμάτη ΒΔ. **Πρέπει πρώτα να αποφασιστεί**
   πώς αντιμετωπίζονται το P1 και μέρος του P2/P4 λόγω του κενού κάλυψης
   δεδομένων (βλ. ⚠️ εύρημα στο Analytics core section πάνω) — δεν προχωράω
   χωρίς αυτή την απόφαση
3. Πραγματικό LLM integration στο `NegotiationAnalysis.create_analysis`
   (OpenAI API call, strict prompt μόνο πάνω σε δοθέν context, temperature=0,
   άρνηση αν λείπουν δεδομένα — βλ. κανόνες LLM integration στο CLAUDE.md)
4. `POST /synthesis` endpoint (context = όλα τα events + scores, `is_synthesis=true`)
5. Ανοιχτή απόφαση: `is_verified=true` σε World Bank/SIPRI-sourced indicators
   (όχι από τη διπλωματική) — βλ. "Data Sources" στο CLAUDE.md, ζήτημα ρητά
   σημειωμένο, όχι επιλυμένο
6. Ανοιχτή απόφαση: ο `analytics` router κάνει `raise HTTPException` απευθείας
   αντί για custom domain exception + handler στο `main.py`, μόνη απόκλιση από
   το πρότυπο των υπόλοιπων routers
7. Κενά test coverage (βλ. πάνω): unit tests για User service, integration
   tests για negotiation-analyses/analytics
8. Τα deferred indicators/event-markers του `SEED_DATA_SPEC.md` (§2.1-2.4,
   βλ. "Future Work" σχόλιο στο seed.py) — προαιρετικό, χαμηλή προτεραιότητα
9. Docker Compose: μόνο η υπηρεσία `db` υπάρχει· λείπουν οι υπηρεσίες `api`/`frontend`
10. README.md δεν έχει γραφτεί ακόμα (ο άνθρωπος-αναγνώστης διαβάζει αυτό, όχι το CLAUDE.md)
11. Μετά: React frontend (`frontend/`, δεν έχει ξεκινήσει ακόμα — δεν υπάρχει καν ο φάκελος)

**Uncommitted αρχεία αυτή τη στιγμή** (session 2026-08-02, μετά Στάδιο 1+2):
`CLAUDE.md`, `PROJECT_PLAN.md`, `PROJECT_STATUS.md`,
`backend/app/models/indicator.py`, `backend/app/models/negotiation_event.py`,
`backend/app/schemas/indicator.py`, `backend/app/schemas/negotiation_event.py`,
`backend/app/scripts/seed.py`, `backend/app/services/analytics.py`,
`backend/requirements.txt`, νέο:
`backend/alembic/versions/b536861761e3_add_confidence_to_indicators_and_.py`

**Ρητά ΟΧΙ τώρα (αποφασισμένο, future work):** live data-refresh endpoint που
καλεί το World Bank API on-demand από FastAPI (ADMIN-only, workflow
`is_verified=false` μέχρι verify) — τεκμηριωμένο ήδη ως "future" στον ΧΡΥΣΟ
ΚΑΝΟΝΑ του CLAUDE.md, καμία αλλαγή δεν χρειάζεται εκεί.

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
