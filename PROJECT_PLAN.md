# PROJECT_PLAN.md — Kosovo Negotiation Analytics

Agent-facing χρονοδιάγραμμα/roadmap. Για το domain model, τους κανόνες και τις
συμβάσεις δες [CLAUDE.md](CLAUDE.md) — αυτό εδώ είναι μόνο "πού είμαστε / τι ακολουθεί".

**Κατάσταση:** αυτό το roadmap είναι πλέον ολοκληρωμένο — backend και frontend
και τα δύο σε παραγωγική μορφή, deployment-ready (Railway prep). Το αρχείο
μένει εδώ ως ιστορικό αρχικού σχεδιασμού· το ένα ανοιχτό σημείο που απομένει
είναι μέρος του Actors feature (§8 παρακάτω). Για το ζωντανό, session-by-session
status δες το [PROJECT_STATUS.md](PROJECT_STATUS.md) — αυτό εδώ ενημερώνεται
μόνο σε επίπεδο milestones.

---

## Status snapshot

| Κομμάτι | Κατάσταση |
|---|---|
| FastAPI app (skeleton, `GET /` health) | ✅ |
| DB connection (`Base`, `get_db()`) | ✅ |
| PostgreSQL via Docker Compose (db + api + frontend, πλήρες stack) | ✅ |
| Alembic migrations, όλες εφαρμοσμένες | ✅ |
| `Country` slice | ✅ ολοκληρώθηκε |
| `User` + JWT auth (`require_admin` σε όλα τα write endpoints) | ✅ ολοκληρώθηκε |
| `Indicator` slice | ✅ ολοκληρώθηκε |
| Business rules / analytics core (Power Index, Power Gap, Window Score, Optimal Agreement/Mutual Compromise Period, Best Moments) | ✅ ολοκληρώθηκε |
| `NegotiationEvent` (+ `event_participants`) | ✅ ολοκληρώθηκε |
| `NegotiationAnalysis` + LLM integration | ✅ ολοκληρώθηκε — Anthropic Claude (`claude-sonnet-4-6`), per-event Q&A + `POST /synthesis` + `POST /compare`, απαντά στη γλώσσα της ερώτησης |
| Seed script | ✅ 12 countries/actors, 111 indicators, 10 negotiation events (E1-E10) |
| P1-P5 validation tests | ✅ 7 tests σε πραγματική ΒΔ — όλα επιβεβαιωμένα, λεπτομέρειες στο [SEED_SOURCE.md](SEED_SOURCE.md) |
| Tests (unit/integration) | ✅ **92 passed** |
| README.md | ✅ πλήρης οδηγός για αξιολόγηση του project |
| Rate limiting, CORS, production env vars (Railway prep) | ✅ |
| Frontend (React dashboard, όλες οι οθόνες) | ✅ ολοκληρώθηκε |
| **Actors feature** — SUPPORTER role, role_description, China/India/OSCE/ICJ, frontend badges | ✅ ολοκληρώθηκε |
| `GET /countries/{id}/events` endpoint | ⏸ δεν έχει υλοποιηθεί ακόμα, βλ. §8 |

Λεπτομέρειες/ανοιχτά ζητήματα (World Bank data sourcing vs ΧΡΥΣΟ ΚΑΝΟΝΑ, analytics
router pattern deviation) στο [PROJECT_STATUS.md](PROJECT_STATUS.md).

## Αποφασισμένα (πρώην ασυνέπειες, ενημερώθηκε το CLAUDE.md)

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

### 1. Country -- ΟΛΟΚΛΗΡΩΘΗΚΕ
Model + migration + repository (CRUD) + service (custom exceptions
`CountryNotFoundError`, `DuplicateCountryNameError`) + schema (Pydantic v2:
`CountryCreate`/`CountryUpdate`/`CountryRead`) + router (`/countries`, full
CRUD) + 19 tests (11 unit με mocked repository, 8 integration με TestClient).
Domain exceptions → HTTP status μέσω `@app.exception_handler` στο `main.py`
(404/409), όχι try/except στο router. Write endpoints είναι **προς το παρόν
ανοιχτά χωρίς auth** — το ADMIN-only gating μπαίνει στο slice 2 μαζί με τα
`get_current_user`/`require_admin` dependencies. **Αυτό είναι το πρότυπο
pattern για όλα τα επόμενα slices.**

### 2. User + Auth -- ΟΛΟΚΛΗΡΩΘΗΚΕ
`User` model (email, hashed_password, role) → JWT login/register →
`get_current_user` / `require_admin` dependencies, εφαρμοσμένα σε όλα τα
write endpoints (Country/Indicator/NegotiationEvent).

### 3. Indicator -- ΟΛΟΚΛΗΡΩΘΗΚΕ
Model (country_id FK, category enum, indicator_type, year, value, unit, source,
is_verified) → CRUD slice. Το "verify" γίνεται μέσω του γενικού
`PUT /indicators/{id}` (ήδη ADMIN-only), όχι ξεχωριστό endpoint.

### 4. Power Index / Power Gap / Window Score / Optimal Periods -- ΟΛΟΚΛΗΡΩΘΗΚΕ
`app/services/analytics.py`, καθαρά ντετερμινιστικό, ΧΩΡΙΣ LLM. Weights:
Economic 40% / Military 40% / Social 20%. Επιπλέον `find_best_moments`
(confidence HIGH/MEDIUM/LOW) πέρα από το αρχικό σχέδιο. Πλήρης μεθοδολογία,
συμπεριλαμβανομένης της σύγκρισης με το CINC: [SEED_SOURCE.md §9](SEED_SOURCE.md).

### 5. NegotiationEvent (+ event_participants) -- ΟΛΟΚΛΗΡΩΘΗΚΕ
Model με τα ZOPA/ripeness/BATNA/red lines πεδία + association table
(event_id, country_id, role) διαχειρίζεται μέσα από το event schema. Business
rule: `economic_weight + military_weight + social_weight == 10` → 422.

### 6. NegotiationAnalysis + LLM integration -- ΟΛΟΚΛΗΡΩΘΗΚΕ
Model + CRUD slice + πραγματικό LLM call. Πάροχος: **Anthropic Claude**
(`claude-sonnet-4-6`, `temperature=0`, JSON response) — αντικατέστησε το
αρχικό σχέδιο για OpenAI (ποτέ υλοποιημένο). Context: δομημένα πεδία event +
Indicators ±2 έτη (Q&A) ή όλα τα events + timeline + optimal periods +
best_moments (synthesis) + participants. `POST /negotiation-analyses`
(per-event Q&A), `POST /synthesis` (γενική ανάλυση) και `POST /compare`
(σύγκριση δύο events). Απαντά στην ίδια γλώσσα με την ερώτηση του χρήστη.
Λεπτομέρειες: PROJECT_STATUS.md.

### 7. Seed script -- ΟΛΟΚΛΗΡΩΘΗΚΕ
`python -m app.scripts.seed` — 12 countries/actors, 111 indicators (μείγμα
πραγματικών τιμών από τη διπλωματική, World Bank API, Freedom House),
10 negotiation events (E1-E10), πεδία `confidence`/`implementation_success`.
Πλήρης πηγή ανά indicator: [SEED_SOURCE.md](SEED_SOURCE.md).

### 7b. Validation tests P1-P5 -- ΟΛΟΚΛΗΡΩΘΗΚΕ
`tests/unit/test_validation_targets.py` — ελέγχει αν ο analytics πυρήνας
αναπαράγει τα ποιοτικά συμπεράσματα Κεφ. 4 της διπλωματικής, σε πραγματική
ΒΔ. Και οι 5 προτάσεις επιβεβαιωμένες ή τεκμηριωμένα rescoped βάσει κάλυψης
δεδομένων· το κεντρικό εύρημα (2013 = optimal window) επιβίωσε πολλαπλές
μεθοδολογικές αναθεωρήσεις. Πλήρες ιστορικό στο PROJECT_STATUS.md.

### 8. Actors feature -- ΣΧΕΔΟΝ ΟΛΟΚΛΗΡΩΘΗΚΕ
Πρόταση από την εξαγωγή δρώντων της διπλωματικής (κεφ. 3.1+3.2, βλ.
[SEED_SOURCE.md](SEED_SOURCE.md) ενότητες 1/4/5/7 για τα raw δεδομένα). Στόχος:
αναδείξει ΠΟΙΟΣ δρώντας κρατούσε τη μόχλευση σε κάθε event (κρίσιμο για το
`/compare`, βλ. SEED_SOURCE.md §7 "μετατόπιση τύπου ισχύος").

Κατάσταση ανά βήμα:
1. Ρόλος `SUPPORTER` στο `ParticipantRole` enum -- ολοκληρώθηκε.
2. Πεδίο `role_description` (Text, nullable) στο `Country` model -- ολοκληρώθηκε.
3. Νέοι δρώντες στο seed (China, India, OSCE, ICJ) -- ολοκληρώθηκε.
4. `event_participants` με τα SUPPORTER links του SEED_SOURCE.md §4 -- ολοκληρώθηκε.
5. **Endpoint `GET /countries/{id}/events`** -- ΔΕΝ υλοποιήθηκε ακόμα. Το μόνο
   ανοιχτό σημείο του roadmap. Δεν υπάρχει σήμερα κανένα "events by
   participant" query σε repository/service/router.
6. LLM context: το synthesis/compare context ήδη περιλαμβάνει όλους τους
   participants (γενικά, όχι ειδικά highlighted SUPPORTER links).
7. Frontend badges ανά ρόλο/`geopolitical_bloc`, `role_description` στην
   οθόνη δρώντα -- ολοκληρώθηκε (`ActorsPage`, `ActorDetailPage`).

### 9. Frontend (React dashboard) -- ΟΛΟΚΛΗΡΩΘΗΚΕ
Dashboard, Actors, Events, Synthesis, Compare -- όλες οι οθόνες.

**Οθόνη Συμπερασμάτων — ιδέες οπτικοποίησης, όπως αρχικά σχεδιάστηκαν.**
Τέσσερις ενότητες, καθεμία δεμένη με υπολογισμένο δεδομένο, όχι στατικό
κείμενο (και οι τέσσερις υλοποιήθηκαν στο Dashboard):
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
