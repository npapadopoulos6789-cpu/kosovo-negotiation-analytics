# PROJECT_PLAN.md — Kosovo Negotiation Analytics

Agent-facing χρονοδιάγραμμα/roadmap. Για το domain model, τους κανόνες και τις
συμβάσεις δες [CLAUDE.md](CLAUDE.md) — αυτό εδώ είναι μόνο "πού είμαστε / τι ακολουθεί".

**Ενημερώθηκε:** 2026-08-02 · **Branch:** `main` · **Τελευταία αλλαγή:**
seed.py αντικαταστάθηκε με πραγματικά δεδομένα (World Bank API + διπλωματική),
analytics core ολοκληρώθηκε

**⚠️ Αυτό το αρχείο είναι το αρχικό roadmap, όχι το ζωντανό status. Για το
ακριβές "πού βρισκόμαστε τώρα" δες το [PROJECT_STATUS.md](PROJECT_STATUS.md),
που ενημερώνεται κάθε session — αυτό εδώ ενημερώνεται μόνο σε milestones.**

---

## Status snapshot

Όλα τα vertical slices του roadmap έχουν κλείσει εκτός από το frontend (#8).

| Κομμάτι | Κατάσταση |
|---|---|
| FastAPI app (skeleton, `GET /` health) | ✅ |
| DB connection (`Base`, `get_db()`) | ✅ |
| PostgreSQL via Docker Compose | ✅ |
| Alembic — 5 migrations, όλες εφαρμοσμένες | ✅ |
| **`Country` slice** | ✅ ολοκληρώθηκε |
| **`User` + JWT auth (`require_admin` σε όλα τα write endpoints)** | ✅ ολοκληρώθηκε |
| **`Indicator` slice** | ✅ ολοκληρώθηκε |
| **Business rules / analytics core** (Power Index, Power Gap, Window Score,
  Optimal Agreement/Mutual Compromise Period, Best Moments) | ✅ ολοκληρώθηκε,
  22 unit tests |
| **`NegotiationEvent` (+ `event_participants`)** | ✅ ολοκληρώθηκε |
| **`NegotiationAnalysis`** | ⚠️ CRUD σκελετός έτοιμος, LLM call ΔΕΝ έχει
  υλοποιηθεί ακόμα (`llm_answer`/`model_used` μένουν `NULL`) |
| **Seed script** | ✅ πραγματικά δεδομένα (World Bank API + διπλωματική) — αλλά
  δεν καλύπτει ακόμα όλο το `SEED_DATA_SPEC.md` (λείπουν 3 events, 2 προτεινόμενα
  πεδία, τα P1-P5 validation tests) |
| `requirements.txt` + `pytest.ini` | ✅ (διορθώθηκε 2026-08-02: έλειπαν
  `bcrypt`/`python-jose`/`email-validator`) |
| Tests (unit/integration) | ✅ **73 passed** — αλλά κενά coverage: όχι unit
  test για User service, όχι integration tests για negotiation-analyses/analytics |
| Docker Compose πλήρες stack (api + frontend services) | ❌ — μόνο `db` υπάρχει |
| README.md (ο άνθρωπος-αναγνώστης) | ❌ — δεν έχει γραφτεί ακόμα |
| Frontend (React dashboard) | ❌ — δεν υπάρχει καν ο φάκελος |

Λεπτομέρειες/ανοιχτά ζητήματα (World Bank data sourcing vs ΧΡΥΣΟ ΚΑΝΟΝΑ, analytics
router pattern deviation) στο [PROJECT_STATUS.md](PROJECT_STATUS.md).

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

### 2. User + Auth ✅ ΟΛΟΚΛΗΡΩΘΗΚΕ
`User` model (email, hashed_password, role) → JWT login/register →
`get_current_user` / `require_admin` dependencies, εφαρμοσμένα σε όλα τα
write endpoints (Country/Indicator/NegotiationEvent).

### 3. Indicator ✅ ΟΛΟΚΛΗΡΩΘΗΚΕ
Model (country_id FK, category enum, indicator_type, year, value, unit, source,
is_verified) → CRUD slice. Το "verify" γίνεται μέσω του γενικού
`PUT /indicators/{id}` (ήδη ADMIN-only), όχι ξεχωριστό endpoint.

### 4. Power Index / Power Gap / Window Score / Optimal Periods ✅ ΟΛΟΚΛΗΡΩΘΗΚΕ
`app/services/analytics.py`, καθαρά ντετερμινιστικό, ΧΩΡΙΣ LLM. Weights:
Economic 40% / Military 40% / Social 20%. 22 unit tests με mocked repositories.
Επιπλέον `find_best_moments` (confidence HIGH/MEDIUM/LOW) πέρα από το αρχικό σχέδιο.

### 5. NegotiationEvent (+ event_participants) ✅ ΟΛΟΚΛΗΡΩΘΗΚΕ
Model με τα ZOPA/ripeness/BATNA/red lines πεδία + association table
(event_id, country_id, role) διαχειρίζεται μέσα από το event schema. Business
rule: `economic_weight + military_weight + social_weight == 10` → 422.

### 6. NegotiationAnalysis + LLM integration ⚠️ ΜΙΣΟΤΕΛΕΙΩΜΕΝΟ
Model + CRUD slice (GET/POST) έτοιμα. **Η πραγματική LLM κλήση ΔΕΝ έχει γραφτεί
ακόμα** — `POST /negotiation-analyses` αποθηκεύει το ερώτημα με `llm_answer=NULL`.
Μένει: LLM service (`temperature=0`, JSON response, context = μόνο δομημένα
πεδία event + Indicators ±1-2 έτη + Power Index/Gap/Window Score/Optimal Periods
+ participants) και το `POST /synthesis` endpoint.

### 7. Seed script ✅ ΟΛΟΚΛΗΡΩΘΗΚΕ (μερικώς πέρα από το αρχικό σχέδιο)
`python -m app.scripts.seed` — 9 countries/actors, 44 indicators (πραγματικές
τιμές World Bank API + Freedom House chart), 7 negotiation events. Το πλήρες
σχέδιο (`SEED_DATA_SPEC.md`) προβλέπει 10 events + 2 νέα πεδία
(`confidence`, `implementation_success`) + validation tests έναντι των
συμπερασμάτων της διπλωματικής — αυτά μένουν, βλ. PROJECT_STATUS.md.

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
