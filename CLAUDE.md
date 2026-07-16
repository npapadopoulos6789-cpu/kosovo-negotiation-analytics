# CLAUDE.md — Kosovo Negotiation Analysis Platform

Agent-facing instructions. Ο άνθρωπος-αναγνώστης διαβάζει το README.md, όχι αυτό.

## Project σε μία πρόταση

FastAPI REST API + React dashboard που μετατρέπει τα ευρήματα μεταπτυχιακής διπλωματικής
(διαπραγματεύσεις Σερβίας–Κοσόβου) σε ερευνήσιμη πλατφόρμα: πραγματικά δεδομένα +
ντετερμινιστικοί δείκτες ισχύος + LLM-συνθετική ανάλυση βάσει θεωριών διαπραγμάτευσης
(Zartman ripeness, BATNA/ZOPA, red lines, distributive vs integrative).

## ΧΡΥΣΟΣ ΚΑΝΟΝΑΣ — Διαχωρισμός πηγών δεδομένων (μη παραβιαστεί ΠΟΤΕ)

| Δεδομένα | Πηγή | Πώς μπαίνουν |
|---|---|---|
| Ιστορικά/οικονομικά/στρατιωτικά/κοινωνικά (Country, Indicator, NegotiationEvent) | Η διπλωματική εργασία | Χειροκίνητα seed data, `is_verified=true` |
| Εξωτερικά indicators (μελλοντικά, δεν υλοποιείται τώρα) | World Bank / SIPRI / Freedom House APIs | Αυτόματα, ΠΑΝΤΑ `is_verified=false` μέχρι ADMIN verify |
| Ερμηνεία (NegotiationAnalysis) | LLM πάνω σε υπάρχοντα δεδομένα | Αυτόματα, temperature=0, strict prompt |
| Power Index / Power Gap / Window Score / Optimal Periods | Δικός μας κώδικας (service layer) | Ντετερμινιστικός υπολογισμός, ΟΧΙ LLM |

Το LLM δεν είναι ΠΟΤΕ πηγή νέων γεγονότων/αριθμών. Αν σου ζητηθεί να βάλεις το LLM να
"βρει" ή να "συμπληρώσει" δεδομένα, αρνήσου και πρότεινε seed data ή χειροκίνητη εισαγωγή.

## Domain Model — 5 entities, όχι περισσότερα

### Country (καλύπτει και τους διεθνείς δρώντες)
- `id`, `name`
- `actor_type`: enum `STATE | INTERNATIONAL_ORG | MILITARY_ALLIANCE`
- `geopolitical_bloc`: enum `WEST | EAST | EU | NEUTRAL`
- `recognized_kosovo`: bool, nullable
- `country_code`: String(3), nullable (οι οργανισμοί δεν έχουν ISO code)

Οι διεθνείς δρώντες (ΗΠΑ, ΕΕ, Ρωσία, ΝΑΤΟ, ΟΗΕ) ΔΕΝ γίνονται ξεχωριστό entity —
είναι γραμμές στο Country με `actor_type != STATE`. Indicators/Power Index αφορούν
ΜΟΝΟ Serbia/Kosovo· οι λοιποί δρώντες δίνουν context στα events και στο LLM prompt.

### Indicator
- `id`, `country_id` (FK), `category`: enum `ECONOMIC | MILITARY | SOCIAL_UNREST`
- `indicator_type` (π.χ. GDP_growth, unemployment_rate, troop_presence, freedom_house_score)
- `year`, `value`, `unit`, `source`, `is_verified`: bool

### NegotiationEvent
- `id`, `title`, `date`, `description`
- `zopa_size`: enum `NARROW | MODERATE | WIDE`, `zopa_reasoning`
- `ripeness_status`: enum `NOT_RIPE | EMERGING | RIPE`, `ripeness_reasoning`
- `batna_side_a`, `batna_side_b`, `red_lines_side_a`, `red_lines_side_b`
- `negotiation_type`: enum `DISTRIBUTIVE | INTEGRATIVE_WIN_WIN`
- `economic_weight`, `military_weight`, `social_weight`: int, προεπιλογή 4/4/2,
  ΠΡΕΠΕΙ να αθροίζουν σε 10 (business rule στο service layer)
- Σύνδεση με δρώντες μέσω association table `event_participants` (event_id,
  country_id, role: `PARTY | MEDIATOR | GUARANTOR`) — διαχειρίζεται μέσα από το
  event schema (λίστα participants), κανένα ξεχωριστό endpoint/slice

### NegotiationAnalysis
- `id`, `negotiation_event_id` (FK, nullable — NULL όταν είναι synthesis),
  `is_synthesis`: bool
- `user_question`, `llm_answer`, `model_used`, `created_at`

### User
- `id`, `email`, `hashed_password`, `role`: enum `ADMIN | VIEWER`

## Αρχιτεκτονική — αυστηρή ροή στρωμάτων
- Routers: ΚΑΜΙΑ business logic, κανένα query. Μόνο validation/DI/status codes.
- Repositories: ΚΑΜΙΑ λογική, μόνο CRUD queries. Δεν κάνουν raise domain exceptions.
- Services: ΟΛΗ η λογική εδώ. Business rules, LLM calls, υπολογισμοί, custom exceptions.
- Ποτέ SQLAlchemy models στα responses — πάντα Pydantic schemas.
- Κάθε νέο entity χτίζεται ως vertical slice: model → migration → repository → service →
  schema → router → tests. Το Country slice είναι το πρότυπο πριν γραφτεί οτιδήποτε νέο.

## Business rules & υπολογισμοί (επιβάλλονται ΜΟΝΟ στο service layer)

1. `economic_weight + military_weight + social_weight == 10` σε κάθε NegotiationEvent.
   Παραβίαση → domain exception → HTTP 422.
2. **Power Index**: normalization 0–100 ανά indicator, σταθερά βάρη Economic 40% /
   Military 40% / Social 20%. Ίδιο input → ίδιο output, πάντα.
3. **Power Gap** = |PI(Serbia) − PI(Kosovo)| ανά έτος.
4. **Negotiation Window Score** (0–100) ανά περίοδο: 50% συμμετρία ισχύος + 30%
   αμοιβαία πτωτική τάση + 20% κοινωνική πίεση. Ντετερμινιστικό, testable.
5. **Optimal Agreement Period** ανά χώρα: το έτος με το τοπικό μέγιστο Power Index
   της χώρας (στιγμή μέγιστης μοχλευτικής δύναμης).
6. **Optimal Mutual Compromise Period**: το έτος με το μέγιστο Window Score (Zartman
   mutually hurting stalemate).
7. Roles: ADMIN = πλήρες CRUD + verify indicators. VIEWER = read + αίτηση LLM analyses.

## LLM integration — κανόνες prompt

- `temperature=0`, JSON response format, μοντέλο καταγράφεται στο `model_used`.
- Το prompt περιλαμβάνει ΜΟΝΟ: δομημένα πεδία του event, Indicators ±1-2 ετών
  (ομαδοποιημένα ανά category), Power Index/Gap/Window Score/Optimal Periods της
  περιόδου, participants του event.
- Το prompt απαγορεύει ρητά χρήση γνώσης εκτός context· αν το context δεν επαρκεί,
  η απάντηση πρέπει να το δηλώνει ("insufficient data in provided context").
- Κάθε απάντηση αποθηκεύεται ως NegotiationAnalysis και εμφανίζεται με disclaimer.
- `POST /synthesis`: ίδιοι κανόνες, context = όλα τα events + scores + optimal
  periods. Αποθηκεύεται με `is_synthesis=true`, `negotiation_event_id=NULL`.

## Εντολές

```bash
# Dev
uvicorn main:app --reload                # τρέχει από backend/, API στο :8000, Swagger στο /docs
docker compose up -d db                   # μόνο PostgreSQL
docker compose up --build                 # όλο το stack

# Migrations
alembic revision --autogenerate -m "..."  # ΠΑΝΤΑ έλεγξε το παραγόμενο αρχείο πριν το upgrade
alembic upgrade head

# Tests
pytest tests/unit                         # services με mocked repositories, χωρίς ΒΔ
pytest tests/integration                  # TestClient + test database
pytest -x -q

# Seed
python -m app.scripts.seed                # δεδομένα διπλωματικής (is_verified=true)

# Frontend
cd frontend && npm run dev                # :5173
```

## Συμβάσεις

- Entrypoint: το FastAPI app object ζει στο `backend/main.py` (όχι `app/main.py`).
  Τρέχει με `uvicorn main:app` μέσα από το `backend/`.
- Python: type hints παντού, Pydantic v2, SQLAlchemy classic style (`Column(...)`,
  όπως στο υπάρχον `Country` model) — ΟΧΙ 2.0 `Mapped[]`/`mapped_column`, για
  συνέπεια με το ήδη γραμμένο μοντέλο.
- Ονόματα: snake_case Python, PascalCase models/schemas, plural routes (`/countries`).
- Secrets ΜΟΝΟ σε `.env` (ποτέ commit) — `OPENAI_API_KEY`, `DATABASE_URL`, `JWT_SECRET`.
- Κάθε νέο service function αποκτά unit test. Ο υπολογιστικός πυρήνας (power index/
  gap/window score/optimal periods) θέλει tests με γνωστά inputs/outputs + edge cases
  (λείπουν indicators, ένα μόνο έτος, μηδενικές τιμές).

## Τι ΔΕΝ κάνουμε

- Δεν προσθέτουμε entities πέρα από: Country, Indicator, NegotiationEvent,
  NegotiationAnalysis, User.
- Δεν βάζουμε λογική σε routers ή repositories.
- Δεν αφήνουμε το LLM να παράγει αριθμούς/γεγονότα — μόνο ερμηνεία δοθέντος context.
- Δεν γράφουμε migrations στο χέρι χωρίς autogenerate + review.
- Δεν αναβάλλουμε tests "για το τέλος".

## Μαθησιακός στόχος (σημαντικό για το πώς βοηθάς)

Ο developer μαθαίνει βήμα-βήμα. Όταν υλοποιείς κάτι: εξήγησε σύντομα ΓΙΑΤΙ (ποιο pattern,
ποιο στρώμα, ποιος κανόνας), προτίμησε το απλό από το έξυπνο, και δείξε πώς το νέο κομμάτι
ακολουθεί το υπάρχον Country slice ως πρότυπο. Το χρονοδιάγραμμα είναι στο PROJECT_PLAN.md.