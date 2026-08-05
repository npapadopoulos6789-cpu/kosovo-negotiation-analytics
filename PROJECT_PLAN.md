# PROJECT_PLAN.md — Kosovo Negotiation Analytics

Agent-facing χρονοδιάγραμμα/roadmap. Για το domain model, τους κανόνες και τις
συμβάσεις δες [CLAUDE.md](CLAUDE.md) — αυτό εδώ είναι μόνο "πού είμαστε / τι ακολουθεί".

**Ενημερώθηκε:** 2026-08-04 · **Branch:** `main` · **Τελευταία αλλαγή:**
LLM integration ολοκληρώθηκε (Anthropic Claude, `POST /synthesis` +
per-event Q&A, πραγματικά live-δοκιμασμένα) + 3ο previous_year bug
βρέθηκε/διορθώθηκε στο analytics endpoint + security fix (committed
`.env`, JWT rotation) — βλ. PROJECT_STATUS.md για πλήρεις λεπτομέρειες

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
| **`NegotiationAnalysis` + LLM integration** | ✅ ολοκληρώθηκε (2026-08-04) —
  Anthropic Claude (`claude-sonnet-4-6`), όχι OpenAI· per-event Q&A +
  `POST /synthesis`, και τα δύο πραγματικά live-δοκιμασμένα |
| **Seed script** | ✅ πλήρες SEED_DATA_SPEC.md set: 10 events (E1-E10), 59
  indicators, `confidence`/`implementation_success` πεδία — μόνο τα
  προαιρετικά "Future Work" indicators του spec (§2.1-2.4) λείπουν ακόμα |
| **P1-P5 validation tests** | ✅ 6 tests, integration-style σε πραγματική ΒΔ.
  P1/P2/P4 rescoped (κάλυψη δεδομένων), P3 επιβεβαιώνεται (μετά από bug fix),
  P5 τεκμηριωμένο ως μη-επιβεβαιωμένο (μεθοδολογικός περιορισμός, όχι bug) |
| `requirements.txt` + `pytest.ini` | ✅ (διορθώθηκε 2026-08-02: έλειπαν
  `bcrypt`/`python-jose`/`email-validator`) |
| Tests (unit/integration) | ✅ **82 passed** — αλλά κενά coverage: όχι unit
  test για User service, όχι integration tests για negotiation-analyses/
  analytics/synthesis (τα LLM calls επιβεβαιώθηκαν live/χειροκίνητα) |
| Docker Compose πλήρες stack (api + frontend services) | ❌ — μόνο `db` υπάρχει |
| README.md (ο άνθρωπος-αναγνώστης) | ❌ — δεν έχει γραφτεί ακόμα |
| **Actors feature** (SUPPORTER role, role_description, China/India/OSCE/ICJ, `GET /countries/{id}/events`) | ❌ — προτεινόμενο, βλ. #8 παρακάτω |
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

### 6. NegotiationAnalysis + LLM integration ✅ ΟΛΟΚΛΗΡΩΘΗΚΕ (2026-08-04)
Model + CRUD slice + πραγματικό LLM call, και τα δύο έτοιμα. Πάροχος:
**Anthropic Claude** (`claude-sonnet-4-6`, `temperature=0`, JSON response) —
απόφαση που αντικατέστησε το αρχικό σχέδιο για OpenAI (ποτέ υλοποιημένο,
μόνο σχόλιο πρόθεσης). Context: δομημένα πεδία event + Indicators ±2 έτη
(Q&A) ή όλα τα events + timeline + optimal periods + best_moments
(synthesis) + participants. `POST /negotiation-analyses` (per-event Q&A)
και `POST /synthesis` (γενική ανάλυση, `is_synthesis=true`) και τα δύο
πραγματικά δοκιμασμένα live. Λεπτομέρειες: PROJECT_STATUS.md.

### 7. Seed script ✅ ΟΛΟΚΛΗΡΩΘΗΚΕ, πλήρες SEED_DATA_SPEC.md σετ
`python -m app.scripts.seed` — 9 countries/actors, 59 indicators (πραγματικές
τιμές World Bank API + Freedom House chart), 10 negotiation events (E1-E10),
πεδία `confidence`/`implementation_success`. Μόνο τα προαιρετικά "Future Work"
indicators του spec §2.1-2.4 λείπουν ακόμα (χαμηλή προτεραιότητα).

### 7b. Validation tests P1-P5 ✅ ΟΛΟΚΛΗΡΩΘΗΚΕ (2026-08-03)
`tests/unit/test_validation_targets.py` — ελέγχει αν ο analytics πυρήνας
αναπαράγει τα ποιοτικά συμπεράσματα Κεφ. 4 της διπλωματικής. Στην πορεία
βρέθηκαν και διορθώθηκαν 2 πραγματικά bugs στο `previous_year` logic του
Window Score (`find_optimal_mutual_compromise_period`, `find_best_moments`)
— άλλαξε πραγματικά αποτελέσματα (2013 έγινε το optimal window αντί για
2023, 2 events ανέβηκαν σε HIGH confidence). Λεπτομέρειες/πραγματικές τιμές
στο PROJECT_STATUS.md.

### 8. Actors feature ❌ ΠΡΟΤΕΙΝΟΜΕΝΟ, δεν έχει ξεκινήσει
Πρόταση από την εξαγωγή δρώντων της διπλωματικής (κεφ. 3.1+3.2, βλ.
[SEED_SOURCE.md](SEED_SOURCE.md) ενότητες 1/4/5/7 για τα raw δεδομένα). Στόχος:
αναδείξει ΠΟΙΟΣ δρώντας κρατούσε τη μόχλευση σε κάθε event (κρίσιμο για το
`/compare`, βλ. SEED_SOURCE.md §7 "μετατόπιση τύπου ισχύος").

Βήματα (σειρά προτεραιότητας):
1. **Νέος ρόλος `SUPPORTER`** στο `ParticipantRole` enum (μαζί με `PARTY`,
   `MEDIATOR`, `GUARANTOR`). Χωρίς αυτόν δεν αποτυπώνεται η γεωπολιτική
   στήριξη χωρίς συμμετοχή στο τραπέζι (π.χ. Russia/China SUPPORTER(Serbia)
   μέσω απειλής βέτο, χωρίς να "μεσολαβούν"). Migration.
2. **Νέο πεδίο `role_description`** (Text, nullable) στο `Country` model —
   μικρό migration. Seed content έτοιμο στο SEED_SOURCE.md §5.
3. **Νέοι δρώντες στο seed** (επιβεβαιωμένα λείπουν σήμερα): China (ήδη
   Country row αλλά 0 event_participants), India, OSCE, ICJ.
4. **Ενημέρωση `event_participants`** με τα SUPPORTER links του SEED_SOURCE.md
   §4 (π.χ. Russia/China SUPPORTER σε Rambouillet, Ψήφισμα 1244, Ahtisaari,
   UDI, Ουάσιγκτον, Οχρίδα — κανένα από αυτά τα links δεν υπάρχει σήμερα).
5. **Endpoint** `GET /countries/{id}/events` — events ενός δρώντα με τον ρόλο
   του σε καθένα. Δεν υπάρχει σήμερα κανένα "events by participant" query σε
   repository/service/router (επιβεβαιωμένο, session 2026-08-05).
6. **LLM context**: το synthesis/compare context να συμπεριλάβει τα
   SUPPORTER links + το SEED_SOURCE.md §7, ώστε το LLM να αναδεικνύει τη
   μετατόπιση στρατιωτική→οικονομική μόχλευση.
7. **Frontend**: badges ανά ρόλο στην οθόνη event· κλικ σε δρώντα →
   `role_description` + λίστα events· χρωματισμός ανά `geopolitical_bloc`.

### 9. Frontend (React dashboard)
Ξεκινάει αφού το API έχει τουλάχιστον Country + Indicator + NegotiationEvent +
Power Index endpoints σταθερά, ώστε να μη χρειάζεται ανασχεδιασμός contracts.

**Οθόνη Συμπερασμάτων — ιδέες οπτικοποίησης** (μεταφέρθηκε από πρώην
`SEED_DATA_SPEC.md` §5). Τέσσερις ενότητες, καθεμία δεμένη με υπολογισμένο
δεδομένο, όχι στατικό κείμενο:
1. **Ασυμμετρία BATNA** — Το Κόσοβο δεν διαθέτει ανεξάρτητη εναλλακτική· η
   ισχύς του είναι δανεική από τη Δύση. *Οπτικοποίηση:* Power Index breakdown
   ανά component (economic/military/social).
2. **Μετασχηματισμός της σερβικής ισχύος** — Από στρατιωτική (προ-1999) σε
   διπλωματική/οικονομική (μετά το 2008). *Οπτικοποίηση:* stacked area chart
   των τριών components της Σερβίας διαχρονικά.
3. **Η ZOPA διευρύνεται, η εφαρμογή αποτυγχάνει** — το κεντρικό παράδοξο (βλ.
   PROJECT_STATUS.md, ενότητα "Validation tests P1-P5").
4. **Το πολιτικό κόστος υπερισχύει του οικονομικού** — Two-level game
   (Putnam): οι εσωτερικές πιέσεις περιορίζουν το win-set. *Οπτικοποίηση:*
   Freedom House score δίπλα στο Window Score — η πτώση του δημοκρατικού
   δείκτη συμπίπτει με τις αποτυχίες εφαρμογής.

Επιπλέον ιδέα από το ίδιο σημείωμα: γράφημα με δύο γραμμές — `Window Score`
(πότε ήταν κατάλληλη η στιγμή) vs `Implementation Success` (0-1, πόσο
εφαρμόστηκε η συμφωνία) — η απόκλιση των δύο γραμμών είναι η οθόνη
Συμπερασμάτων.

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
