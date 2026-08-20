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

_Τελευταία πλήρης ανανέωση: 2026-08-20. Session: (1) power-index-breakdown_
_endpoint (economic/military/social/power_index breakdown, ίδιο pattern με_
_calculate_power_index), (2) CORS middleware στο backend/main.py για το_
_React dev server (:5173), (3) καθάρισμα `__pycache__` από git tracking_
_(8 αρχεία, το gitignore ήδη το κάλυπτε), (4) **ξεκίνησε το frontend**:_
_Vite + React + TypeScript scaffold (`frontend/`, `npm create vite@latest`),_
_deps `react-router-dom`/`@tanstack/react-query`/`recharts`, dev server_
_επιβεβαιωμένος στο :5173, (5) πρώτο κομμάτι του API layer -- μόνο Country_
_resource προς το παρόν: `api/types.ts`, `api/client.ts` (γενικός fetch_
_wrapper, ΧΩΡΙΣ path-normalization λογική -- βλ. σημείωση παρακάτω),_
_`api/countries.ts` (πλήρες CRUD), `hooks/useCountryLookup.ts` (react-query,_
_Map<id, Country>, memoized). `pytest -q` στο `backend/`: **25/25 unit_
_analytics tests passed** (δεν ξανατρέχτηκε ολόκληρο το suite σήμερα)._
_`tsc --noEmit` καθαρό στα νέα frontend αρχεία. (6) `QueryClientProvider`_
_στηθεί στο `main.tsx` (ένα QueryClient σε module scope, τυλίγει το <App/>_
_μέσα στο StrictMode) -- το `useCountryLookup` είναι πλέον λειτουργικό_
_end-to-end, επιβεβαιωμένο με `tsc --noEmit` + dev server smoke test (200_
_OK στο :5173). Τελευταίο pushed commit: `cb9ea97` ("Add API client layer_
_for Country resource"). `frontend/src/main.tsx` (QueryClientProvider) είναι_
_ΑΚΟΜΑ uncommitted._

**Frontend trailing-slash gotcha (κρίσιμο, μη το ξαναχάσεις):** το backend_
_ΔΕΝ έχει ενιαία σύμβαση. `/countries` (list/create) ΧΩΡΙΣ trailing slash,_
_αλλά `/indicators/`, `/negotiation-events/`, `/negotiation-analyses/`_
_(list/create) ΜΕ trailing slash. Λάθος convention σε client → 307 redirect_
_→ σπάει το CORS preflight cross-origin με confusing error. Το πλήρες_
_reference table είναι στο σχόλιο στο τέλος του `frontend/src/api/client.ts`._
_Κάθε επόμενο resource module πρέπει να κοιτάξει το αντίστοιχο_
_`backend/app/api/*.py`, όχι να υποθέσει._

**Ακόμα δεν έγινε (frontend):** routing (react-router-dom είναι installed,_
_δεν έχει στηθεί), layout, resource modules για Indicator/NegotiationEvent/_
_Analytics/Synthesis, κανένα UI component ακόμα (μόνο το default Vite_
_starter page στο App.tsx).

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
  τελευταίο commit `358d70e`, όλα pushed (`origin/main` == `HEAD`)
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
   **LLM integration ΟΛΟΚΛΗΡΩΘΗΚΕ (2026-08-04, βλ. ενότητα "LLM integration"
   παρακάτω) — `POST /negotiation-analyses` κάνει πλέον πραγματικό call στο
   Claude API.** `llm_answer` αποθηκεύει το πλήρες JSON response ως string,
   `model_used="claude-sonnet-4-6"`.
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
  4 νέα έτη (1998/2000/2018/2020) προστέθηκαν για τα validation tests P1-P5.
- **Κάλυψη δεδομένων (επιβεβαιωμένη μέσω κώδικα, όχι εκτίμηση):** το
  `calculate_power_index` απαιτεί exact-year match ΚΑΙ στις 3 κατηγορίες.
  Πλήρες Power Index υπάρχει ΓΙΑ ΚΑΙ ΤΙΣ ΔΥΟ χώρες ΜΟΝΟ στα
  **{2005, 2007, 2013, 2023}** (το Freedom House/social δεν έχει καμία τιμή
  πριν το 2005 — αυτό είναι το gating constraint, όχι οι υπόλοιπες
  κατηγορίες). Οδήγησε στο rescoping 3 από τα 5 validation tests, βλ. §
  "Validation tests P1-P5" παρακάτω.
- 🐛 **2 πραγματικά bugs βρέθηκαν και διορθώθηκαν (2026-08-03) στο
  `previous_year` του Window Score:** το `find_optimal_mutual_compromise_period`
  ΚΑΙ το `find_best_moments` χρησιμοποιούσαν σαν "προηγούμενο έτος" απλά το
  προηγούμενο στοιχείο της αραιής λίστας `KEY_YEARS` (συχνά χωρίς δεδομένα),
  μηδενίζοντας αθόρυβα το `trend_score` (30% βάρος στο Window Score) στις
  περισσότερες περιπτώσεις. Νέο helper `_most_recent_year_with_data()` το
  διορθώνει και στα δύο σημεία (walk-back στο `KEY_YEARS` μέχρι να βρεθεί
  έτος με Power Index και για τις δύο χώρες). **Επίδραση στα αποτελέσματα:**
  - `find_optimal_mutual_compromise_period(Serbia, Kosovo)`: **2023 → 2013**
    (window_score 61.98, οριακά πάνω από το 59.07/61.79 του 2023) — το P3 της
    διπλωματικής επιβεβαιώνεται πλέον σωστά
  - `find_best_moments`: το confidence του Brussels Agreement (2013) και του
    Ohrid Agreement (2023) ανέβηκε από MEDIUM σε **HIGH** (window_score
    πέρασε το `BEST_MOMENT_THRESHOLD=60.0`)
  - Regression tests προστέθηκαν και για τα δύο σημεία
- 🐛 **3ο ίδιο bug pattern βρέθηκε και διορθώθηκε (2026-08-04) στο ΙΔΙΟ το
  `GET /analytics/window-score/{year}` endpoint** (`app/api/analytics.py`):
  το `previous_year` ήταν optional query param με default `None` — αν ο
  caller δεν το έδινε, το trend_score μηδενιζόταν αθόρυβα (57.34 αντί
  61.98 για το 2013), ενώ το `/optimal-mutual-compromise` για το ΙΔΙΟ έτος
  έδινε 61.98 — δύο endpoints διαφωνούσαν για την ίδια τιμή. Εντοπίστηκε
  σε συστηματικό health-check πριν το LLM integration (βλ. "Backend
  health-check" παρακάτω). Fix: όταν `previous_year is None` ΚΑΙ το έτος
  είναι μέσα στο `KEY_YEARS`, το endpoint τώρα αυτο-υπολογίζει με το ίδιο
  `_most_recent_year_with_data` helper (καμία νέα helper function).
  Ρητό override από τον caller συνεχίζει να δουλεύει. Νέο regression test
  `test_window_score_endpoint_autocomputes_previous_year`
  (`test_validation_targets.py`) επιβεβαιώνει ότι και τα 3 analytics
  endpoints (`window-score`, `optimal-mutual-compromise`, `best-moments`)
  συμφωνούν πλέον για το 2013 (61.98).

### Backend health-check (2026-08-03/04, πριν το LLM integration)
Συστηματικός έλεγχος σε 6 ενότητες πριν προστεθούν νέα features (πλήρες
reset ΒΔ → migrate → seed → business rules → analytics determinism →
auth roles → πλήρες test suite → API surface). Αποτέλεσμα: όλα ✓ εκτός
από το Finding A παραπάνω (ήδη διορθωμένο). Δευτερεύοντα ευρήματα (όχι
bugs, απλές παρατηρήσεις):
- Η ΒΔ έχει 10 events (E1-E10 του `SEED_DATA_SPEC.md`), όχι 7-8 όπως
  περιέγραφε το παλαιότερο `thesis_seed_data.md` — αναμενόμενο, το
  `seed.py` ακολουθεί το πιο πρόσφατο/λεπτομερές spec.
- `/countries` (χωρίς trailing slash) vs `/indicators/`,
  `/negotiation-events/`, `/negotiation-analyses/` (με trailing slash) —
  ασυνέπεια σύμβασης routes, όχι σφάλμα λειτουργίας, δεν διορθώθηκε.

### Validation tests P1-P5 (`tests/unit/test_validation_targets.py`, 6 tests)
Integration-style πάνω στην ήδη-γεμάτη ΒΔ (πραγματικό `SessionLocal`, όχι
mocked) — απαιτεί να έχει τρέξει `python -m app.scripts.seed` πρώτα.
Ελέγχει αν ο ντετερμινιστικός πυρήνας αναπαράγει τα ποιοτικά συμπεράσματα
Κεφ. 4 της διπλωματικής (αρχικά διατυπωμένο ως `SEED_DATA_SPEC.md` §4.1,
πλέον μεταφερμένο εδώ — βλ. SEED_SOURCE.md για το υπόλοιπο του πρώην
SEED_DATA_SPEC.md).

**Αρχικές υποθέσεις (πριν γραφτεί το test, ό,τι περίμενα να δείξει ο
κώδικας) → Πραγματικό εύρημα (μετά το testing).** Κρατιέται ως ζεύγος
σκόπιμα — δείχνει τη μέθοδο (τι υπόθεσα πριν το τεστάρω), όχι μόνο το
τελικό αποτέλεσμα:

| # | Πρόταση διπλωματικής | Αρχική υπόθεση (τι έπρεπε να δείξει ο κώδικας) | Πραγματικό εύρημα | Κατάσταση |
|---|---|---|---|---|
| P1 | Η ισχύς της Σερβίας καταρρέει το 1999 | Power Index Serbia: απότομη πτώση 1998→1999 | 53.65 → 27.53 (rescoped σε economic-only, βλ. παρακάτω) | ✅ επιβεβαιώνεται |
| — | (diagnostic) πλήρες PI unavailable πριν το 2005 | — | `None`, `None` | ✅ τεκμηριωμένο, όχι bug |
| P2 | Η Σερβία ανασυγκροτείται μετά το 2000 | Ανοδική τάση Power Index Serbia 2000-2008 | 46.12 → 46.38 (rescoped σε 2005→2007) | ✅ επιβεβαιώνεται |
| P3 | Το 2013 είναι η στιγμή «ωρίμανσης» | `calculate_window_score` δίνει τοπικό μέγιστο στο 2013 | 2013 (61.98) > 2023 (61.79) | ✅ επιβεβαιώνεται (μετά το bug fix) |
| P4 | Η ισχύς του Κοσόβου ενισχύεται μετά το 2018 | Μείωση Power Gap 2018-2023 | 8.22 → 5.65 (rescoped σε 2013→2023) | ✅ επιβεβαιώνεται |
| P5 | Το Κόσοβο δεν έχει ανεξάρτητη BATNA | Το military+economic component του Κοσόβου παραμένει χαμηλό παρά την ανοδική πορεία του social | economic 68.33→80.23 (ΥΨΗΛΟ), military 55→15 (φθίνον, αμφίσημη κατεύθυνση), social 27.5→38.0 | ⚠️ ΔΕΝ επιβεβαιώνεται — μεθοδολογικός περιορισμός, όχι απόδειξη έλλειψης |

**Best Moments — αναμενόμενη έξοδος (αρχική υπόθεση):** το
`find_best_moments()` έπρεπε να επιστρέψει 2013 και 2023 ως κορυφαία
παράθυρα ευκαιρίας (WIDE ZOPA + RIPE + μειούμενο Power Gap + υψηλή
οικονομική εξάρτηση Σερβίας από ΕΕ). **Εύρημα:** επιβεβαιώνεται — και τα
δύο ανέβηκαν σε confidence=HIGH μετά το bug fix του `previous_year` (βλ.
🐛 παραπάνω).

**Optimal Periods — αναμενόμενη έξοδος (αρχική υπόθεση):** δύο διακριτές
περίοδοι, 2011-2013 (διάλογος Βελιγραδίου-Πρίστινας → Βρυξέλλες) και
2022-2023 (μετά την κρίση πινακίδων → Οχρίδα). **Εύρημα:** συνεπές με το
`find_optimal_mutual_compromise_period` = 2013.

**Το κεντρικό παράδοξο (αρχική υπόθεση, επιβεβαιωμένη):** ο Power Index
και το Window Score δείχνουν ότι οι συνθήκες ωρίμασαν (2013, 2023), αλλά
οι συμφωνίες δεν εφαρμόζονται πλήρως (`implementation_success` 0.3 και
0.2 αντίστοιχα, όχι κοντά στο 1.0) — το χάσμα ανάμεσα σε «τι λέει ο
δείκτης» και «τι έγινε» είναι το εύρημα, όχι bug του δείκτη.

**P1/P2/P4 rescoped** επειδή το πλήρες Power Index δεν είναι υπολογίσιμο
πριν το 2005 (Freedom House gate) ή στο 2018/2020 (χάσμα Serbia-Kosovo
overlap) — τα rescoped tests συγκρίνουν το διαθέσιμο υποσύνολο δεδομένων,
όχι ολόκληρο το αρχικό εύρος ετών του πρωτότυπου P1/P2/P4.

**P5 δεν επιβεβαιώνεται** — όχι επειδή λείπουν δεδομένα, αλλά επειδή το
normalization σχέδιο δεν πιάνει "απόλυτη οικονομική ισχύ" (μετράει μόνο
ρυθμό ανάπτυξης/ανεργία, όπου μικρές οικονομίες βαθμολογούνται ψηλά
ανεξαρτήτως μεγέθους) και το military indicator (troop_presence_index) έχει
αμφίσημη κατεύθυνση ερμηνείας (λιγότερη ξένη στρατιωτική παρουσία θα
έπρεπε εννοιολογικά να σημαίνει ΠΕΡΙΣΣΟΤΕΡΗ αυτονομία, όχι λιγότερη).
`test_kosovo_indicator_breakdown_documented` καταγράφει τις τιμές χωρίς
normative assertion — δεν είναι bug, είναι όριο σχεδιασμού του δείκτη.

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

### 🔒 Security fix (2026-08-04): backend/.env ήταν committed+pushed
`backend/.env` ήταν ήδη tracked στο git ΚΑΙ pushed στο `origin/main` από
δύο παλαιότερα commits (`c9617c2`, `cee82a1`) — το `.gitignore` δεν
αποσυνδέει αναδρομικά αρχεία που ήταν ήδη tracked πριν προστεθεί το
pattern. Αποτέλεσμα: `DATABASE_URL` και `JWT_SECRET_KEY` ήταν ήδη
εκτεθειμένα στο GitHub history πριν καν ξεκινήσει αυτό το session.
Εντοπίστηκε ενώ γινόταν το ANTHROPIC_API_KEY setup (θα προστίθετο ΚΙ
ΑΥΤΟ στο ίδιο tracked αρχείο αν δεν σταματούσαμε).
**Διόρθωση (commit `9bc8be5`):** `git rm --cached backend/.env`
(σταματά το tracking, το τοπικό αρχείο μένει), `JWT_SECRET_KEY`
rotated σε νέο τυχαίο token (invalidates όλα τα παλιά JWT). Το git
ιστορικό ΔΕΝ ξαναγράφτηκε (ρητή απόφαση — το παλιό secret παραμένει
ορατό στο history/GitHub, αλλά δεν έχει πλέον πρακτική αξία μετά το
rotation). `ANTHROPIC_API_KEY` ΠΟΤΕ δεν μπήκε σε commit.

### Seed script (`app/scripts/seed.py`) — ενημερώθηκε 2026-08-02/03/04 βάσει SEED_DATA_SPEC.md
9 countries/actors, **59 indicators**, **10 negotiation events (E1-E10, πλήρες
σετ του spec)**. Ρητές αποφάσεις αυτής της αναθεώρησης (όχι τυφλή υιοθέτηση
του spec):
- **2026-08-03: +8 Serbia indicators** (`GDP_growth`/`unemployment_rate` για
  1998, 2000, 2018, 2020, confidence=EXACT) — τιμές από live World Bank API
  query, ζητήθηκαν για να καλύψουν τα νέα `KEY_YEARS`. Επιβεβαιώθηκε ότι οι
  ήδη υπάρχουσες τιμές ταιριάζουν ψηφίο-προς-ψηφίο με το live API πριν
  προστεθούν οι νέες (αξιοπιστία πηγής).
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
- **2026-08-04, από ανασκόπηση `thesis_seed_data.md`** (νέο αρχείο, μη
  committed, περιείχε ένα παλαιότερο/χοντρικότερο draft σχεδόν πλήρως
  ήδη απορροφημένο στο `SEED_DATA_SPEC.md`/`seed.py`): εμπλουτίστηκε
  ΜΟΝΟ το `description` του E4 ("Standards Before Status") ώστε να
  αναφέρει τις εθνοτικές ταραχές του 2004 (πυρπόληση σερβικών εκκλησιών,
  εκτοπισμός, UNMIK έχασε προσωρινά τον έλεγχο) — καμία αλλαγή σε
  ripeness/zopa/batna/weights/negotiation_type. Απόφαση: το
  `political_status` (Kosovo 1999-2007 = `INTERNATIONAL_ADMINISTRATION`
  υπό UNMIK, τεκμηριωμένο από τη διπλωματική) μπαίνει ΜΟΝΟ ως context
  στο system prompt του LLM (βλ. ενότητα "LLM integration" παρακάτω),
  ΟΧΙ ως νέο πεδίο/migration στο `Country` model.

### LLM integration (2026-08-04) — ΟΛΟΚΛΗΡΩΘΗΚΕ: Anthropic Claude, όχι OpenAI
**Απόφαση παρόχου:** Το CLAUDE.md/PROJECT_STATUS ανέφεραν μέχρι τώρα OpenAI
(π.χ. "OPENAI_API_KEY" στα secrets) — αυτό ήταν απλώς πρόθεση σε σχόλιο,
ποτέ υλοποιημένο. Αποφασίστηκε ρητά **Anthropic Claude API**
(`claude-sonnet-4-6`, `temperature=0`) αντ' αυτού. Το CLAUDE.md
ενημερώθηκε (secrets: `ANTHROPIC_API_KEY` αντί `OPENAI_API_KEY`).

**Νέα αρχεία:**
- `app/core/config.py` — κεντρικό `load_dotenv()` + `DATABASE_URL`/
  `JWT_SECRET_KEY`/`ANTHROPIC_API_KEY`. `database.py`/`security.py`
  refactored να διαβάζουν από εδώ (καμία λειτουργική αλλαγή, ίδιο public
  API, επιβεβαιώθηκε με πλήρες pytest + `alembic current`).
- `app/services/llm_prompts.py` — τα 2 system prompts (καθαρά constants,
  καμία λογική), εγκεκριμένα λέξη-λέξη σε ξεχωριστή φάση σχεδιασμού πριν
  γραφτεί οποιοσδήποτε κώδικας κλήσης. Κοινό preamble (methodology PI/
  Gap/Window Score, ρητός κανόνας `null` = "δεν υπάρχει πηγή" ΟΧΙ μηδέν,
  `political_status` context για Kosovo 1999-2007, απαγόρευση εξωτερικής
  γνώσης, απαγόρευση κατασκευής δηλώσεων προσώπων) + task-specific μέρος
  για Q&A και για synthesis (ρητή εντολή σύγκρισης ποσοτικού/ποιοτικού +
  ρητή εντολή ΜΗ υπερδιατύπωσης σύγκλισης, ώστε το P5 -μη επιβεβαιωμένο-
  να μην "εξαφανιστεί" σε αισιόδοξη γλώσσα).
- `app/services/llm_client.py` — λεπτό wrapper πάνω στο Anthropic SDK.
  `LLMCallError` καλύπτει ΚΑΘΕ αποτυχία (network/auth/rate-limit/μη-έγκυρο
  JSON) — ο caller δεν αποθηκεύει ΠΟΤΕ μισή εγγραφή όταν σηκωθεί.
  `_strip_code_fence` αφαιρεί τυχόν ` ```json ` wrapping. `MAX_TOKENS=8192`
  (ανέβηκε από 2048 αφού το πρώτο πραγματικό synthesis call έκοψε το JSON
  στη μέση — `Unterminated string`). Print statement (ΟΧΙ persisted, ΟΧΙ
  νέο πεδίο) τυπώνει `input_tokens`/`output_tokens`/`max_tokens` σε κάθε
  call, ώστε να φαίνεται στο terminal αν το όριο είναι άνετο.
- `app/api/synthesis.py` — `POST /synthesis`. Μηδενική διπλή λογική: απλά
  φτιάχνει `NegotiationAnalysisCreate(negotiation_event_id=None, ...)` και
  καλεί το ΙΔΙΟ `create_analysis` — το `is_synthesis=True` ήδη γινόταν
  αυτόματα όταν `negotiation_event_id is None`.

**Αλλαγές σε υπάρχοντα:**
- `app/services/negotiation_analysis.py` — `create_analysis` κάνει τώρα
  πραγματικό LLM call αντί για placeholder. Context builders:
  `_build_event_context` (Q&A: το event + participants + Indicators
  Serbia/Kosovo ±2 έτη ομαδοποιημένα ανά category + Power Index/Gap/
  Window Score/Optimal Periods της περιόδου) και `_build_synthesis_context`
  (όλα τα 10 events + timeline πάνω σε `KEY_YEARS` + Optimal Periods +
  `find_best_moments` — έτοιμος convergent-validity έλεγχος, ιδανικό
  υλικό σύγκρισης). Το `window_score` στο context χρησιμοποιεί το ΙΔΙΟ
  auto-compute `previous_year` pattern με το Finding A fix, ώστε το
  context να συμφωνεί με τα analytics endpoints.
- `app/schemas/negotiation_analysis.py` — νέο `SynthesisCreate`
  (`user_question: str`, τίποτα άλλο).
- `main.py` — registered `synthesis_router`, νέος exception handler
  `LLMCallError` → 502 (upstream/parse failure, όχι δικό μας σφάλμα).

**Πραγματικά επιβεβαιωμένο live (όχι μόνο mocked tests):**
- Smoke test (`app/scripts/test_llm.py`) πέτυχε πρώτο.
- 1 πραγματικό synthesis call: πρώτη προσπάθεια απέτυχε (502, JSON
  κόπηκε στη μέση με `MAX_TOKENS=2048`) — ανέβηκε σε 8192, ξανατρέχτηκε,
  πέτυχε καθαρά (10.499 χαρακτήρες, JSON parse OK, 10/10 events στο
  `quantitative_qualitative_comparison`, `answer_certainty=MEDIUM`,
  σωστά ρητή αναφορά του χάσματος ωρίμανση/εφαρμογή στο `central_finding`
  για 2013/2023).
- 1 πραγματικό per-event Q&A call (event 1): 201, `input: 2674, output:
  1540 (max_tokens=8192)` στο log — άνετο περιθώριο.
- Και τα δύο test records σβήστηκαν χειροκίνητα μετά την επιβεβαίωση
  (δεν υπάρχει DELETE endpoint για `NegotiationAnalysis` — σκόπιμο,
  διαγράφηκαν απευθείας μέσω `SessionLocal`).

**Tests:** `tests/unit/test_negotiation_analysis_service.py` ξαναγράφτηκε
πλήρως mocked (`FakeCountryRepository`, `FakeIndicatorRepository`,
`FakeAnalyticsService` stub, `fake_llm_call` — ΚΑΝΕΝΑ πραγματικό API call
μέσα από pytest). 6 tests, +1 νέο
(`test_create_analysis_does_not_save_when_llm_call_fails` — επιβεβαιώνει
ότι `LLMCallError` δεν αφήνει μισή εγγραφή).

**Ανοιχτό/μελλοντικό:** το `output_tokens`/`input_tokens` μόνο τυπώνεται
στο terminal, δεν αποθηκεύεται πουθενά (σκόπιμο, όχι θέλαμε migration) —
αν χρειαστεί ιστορικό tracking αργότερα, θέλει ρητή απόφαση για νέο
πεδίο/πίνακα.

### Tests
`backend/tests/`: 6 unit test files (fake repositories/monkeypatch, χωρίς
πραγματική ΒΔ: country, indicator, negotiation_event, negotiation_analysis
[πλήρως mocked ΚΑΙ το LLM call, βλ. "LLM integration" παραπάνω], analytics)
+ `test_validation_targets.py` (**integration-style, πραγματική ΒΔ μέσω
`SessionLocal`, όχι mocked** — μοναδική εξαίρεση στο πρότυπο, 7 tests πια
μετά το νέο regression test του Finding A) + 3 integration test files
(πραγματικά HTTP requests μέσω `TestClient` σε SQLite in-memory: country,
indicator, negotiation_event). Fixtures στο `conftest.py`: `client`
(χωρίς auth, για GET-only tests) και `admin_client` (κάνει register+login
ADMIN αυτόματα, βάζει `Authorization` header). Σύνολο: **82 passed**.

**Κενά στο test coverage** (εντοπίστηκαν 2026-08-02, δεν διορθώθηκαν ακόμα —
βλ. αναλυτικά στο "Επόμενο βήμα" #3 παρακάτω): `User`/auth service χωρίς
δικό του unit test file, καμία integration test file για negotiation-
analyses/analytics/synthesis endpoints.

**Ολοκληρώθηκαν αυτό το session (πρώην "Επόμενο βήμα"):**
- ~~Push στο GitHub~~ ✅ όλα committed ΚΑΙ pushed, `origin/main` == `HEAD`
- ~~Πραγματικό LLM integration~~ ✅ Anthropic Claude, όχι OpenAI (βλ. "LLM
  integration" παραπάνω)
- ~~`POST /synthesis` endpoint~~ ✅ υλοποιήθηκε, πραγματικό call επιβεβαιώθηκε
- ~~`political_status`/thesis_seed_data.md αποφάσεις~~ ✅ context-only,
  E4 description εμπλουτίστηκε

**Επόμενο βήμα (ό,τι μένει ανοιχτό):**
1. Ανοιχτή απόφαση: `is_verified=true` σε World Bank/SIPRI-sourced indicators
   (όχι από τη διπλωματική) — βλ. "Data Sources" στο CLAUDE.md, ζήτημα ρητά
   σημειωμένο, όχι επιλυμένο
2. Ανοιχτή απόφαση: ο `analytics` router κάνει `raise HTTPException` απευθείας
   αντί για custom domain exception + handler στο `main.py`, μόνη απόκλιση από
   το πρότυπο των υπόλοιπων routers
3. Κενά test coverage: unit tests για User service, integration tests για
   negotiation-analyses/analytics/synthesis endpoints (τα πραγματικά LLM
   calls επιβεβαιώθηκαν χειροκίνητα/live, όχι μέσω αυτοματοποιημένου
   integration test)
4. Μικρή ασυνέπεια σύμβασης: `/countries` χωρίς trailing slash vs τα
   υπόλοιπα routers με trailing slash (εντοπίστηκε στο health-check,
   χαμηλή προτεραιότητα)
5. `output_tokens`/`input_tokens` μόνο log, όχι persisted — απόφαση αν
   χρειάζεται ιστορικό tracking αργότερα
6. Τα deferred indicators/event-markers του πρώην `SEED_DATA_SPEC.md` (§2.1-2.4,
   πλέον SEED_SOURCE.md §3, βλ. "Future Work" σχόλιο στο seed.py) — προαιρετικό,
   χαμηλή προτεραιότητα. **Γνωστό κενό, να ελεγχθεί ρητά στη "Δουλειά Β" (έλεγχος
   βάσης):** τουλάχιστον 3 indicators που το SEED_DATA_SPEC §6 συζήτησε ως προς
   το πώς θα μπουν, δεν μπήκαν ΚΑΘΟΛΟΥ ακόμα στο seed —
   `eu_preaccession_funds` (ασυμφωνία IPA 2,79δις vs 2,2δις, απόφαση ήταν
   θεωρητική), Kosovo `GDP_per_capita`/`GDP_per_capita_USD` (EUR-2003 vs USD
   split), και η ανεργία Κοσόβου 2000 (11,5% ασυμφωνία, το φίλτρο
   `is_verified=false` δεν χρειάστηκε ποτέ γιατί η τιμή απλά δεν seed-άρθηκε).
   Λεπτομέρειες/status ανά indicator: SEED_SOURCE.md §3 και §8.
7. Docker Compose: μόνο η υπηρεσία `db` υπάρχει· λείπουν οι υπηρεσίες `api`/`frontend`
8. README.md δεν έχει γραφτεί ακόμα (ο άνθρωπος-αναγνώστης διαβάζει αυτό, όχι το CLAUDE.md)
9. Μετά: React frontend (`frontend/`, δεν έχει ξεκινήσει ακόμα — δεν υπάρχει καν ο φάκελος)

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
- **Πάντα έλεγχος `git status`/`git log -- <αρχείο>` πριν υποθέσεις ότι ένα
  `.gitignore`-listed αρχείο είναι πράγματι untracked** — το gitignore δεν
  ισχύει αναδρομικά, ένα `.env` μπορεί να είναι ήδη committed+pushed από
  πολύ παλιά (ακριβώς αυτό συνέβη 2026-08-04, βλ. "Security fix")
- Στο Windows/Git Bash: `/tmp/...` paths δεν είναι πάντα ορατά με το ίδιο
  path σε native Windows Python (χρειάζεται `cygpath -w` για μετατροπή) —
  και `print()`/stdout redirect με ελληνικά+ειδικούς χαρακτήρες (π.χ. ∅)
  σκάει με `UnicodeEncodeError` σε cp1253 console αν δεν γραφτεί απευθείας
  σε αρχείο με `encoding="utf-8"`
- Μετά από `docker compose down -v`, όποιο uvicorn process έτρεχε ήδη
  κρατάει νεκρές DB connections στο pool (η Postgres "κάτω από τα πόδια
  του" άλλαξε) — πάντα kill+restart το server μετά από DB reset, όχι μόνο
  μετά από αλλαγή κώδικα
- FastAPI routers: πρόσεχε trailing slash ασυνέπειες μεταξύ routers
  (`/countries` vs `/negotiation-events/`) — 307 redirect αντί για το
  αναμενόμενο status code αν χτυπήσεις το λάθος path με `curl` (δεν
  ακολουθεί redirects by default χωρίς `-L`)
