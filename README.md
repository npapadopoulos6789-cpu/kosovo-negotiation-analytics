# Kosovo Negotiation Analytics

A research platform on the Serbia–Kosovo negotiations (1989–2023): turns the
findings of a postgraduate thesis into an interactive dashboard, combining
real historical/economic/military/social data with deterministic power
indicators (Power Index, Window Score) and LLM-assisted interpretation
grounded in negotiation theory (Zartman ripeness, BATNA/ZOPA, red lines,
distributive vs. integrative negotiation).

## About this project

This project is built on my master's thesis, *"Η Γεωπολιτική και Οικονομική
Διάσταση της Ανεξαρτησίας του Κοσόβου: Διαπραγματεύσεις και Προοπτικές
Συνεργασίας"* ("The Geopolitical and Economic Dimension of Kosovo's
Independence: Negotiations and Prospects for Cooperation") -- Nikolaos
Angelos Papadopoulos, Athens University of Economics and Business (AUEB),
School of Economic Sciences, Department of International and European
Economic Studies (Postgraduate Program).

The thesis analyzed the Serbia-Kosovo negotiations qualitatively, in depth --
ZOPA, BATNA, Zartman ripeness, red lines, and so on. I wanted to see whether
those qualitative findings actually agreed with real, measurable data --
not just assumptions, but numbers.

So I gathered quantitative indicators (economic, military, social) from
public sources -- the World Bank API (GDP growth, unemployment), Freedom
House (political stability), and other public datasets -- and combined them
into a composite indicator of my own design, the "Power Index" (40% economy
/ 40% military / 20% social stability), computed with my own, purely
deterministic code -- not AI-generated numbers.

I didn't want a static PDF full of charts. I wanted the reader to be able to
explore the negotiations themselves interactively -- to see which year was
actually ripe for agreement, compare events against each other, ask their
own questions.

On top of this structured data (never in a vacuum), I use an LLM (Claude) to
connect the numbers to the theory -- to explain why a given period was, or
wasn't, ripe, by combining the Power Index/Window Score with negotiation
theory concepts (ZOPA, BATNA, ripeness). The LLM never invents data -- it
answers strictly from what already exists on the platform.

## Beyond this case study

The data model itself isn't locked to Serbia and Kosovo -- Country, Indicator,
and NegotiationEvent are built around general negotiation-theory concepts
(ZOPA, BATNA, ripeness, negotiation type), not this dispute specifically. If I
added qualitative coding from another case study -- a different geopolitical
conflict or negotiation -- I could run the same theoretical analysis on it:
add the new actors (POST /countries), their quantitative data (POST
/indicators), and my own qualitative coding of events (POST
/negotiation-events). The Power Index and Window Score would compute
automatically, no code changes needed, since they operate generically on
country_id rather than being hardcoded to Serbia/Kosovo.

Two things wouldn't generalize automatically today, though, and I want to be
upfront about that:
- The frontend (Dashboard charts, `useCountryLookup`) is currently hardcoded
  to look up "Serbia"/"Kosovo" by name -- it would need adapting for a
  different country pair or case study.
- The LLM's system prompt contains specific historical context (Kosovo's
  UNMIK administration, 1999-2007) tailored to this case study -- a different
  case would need its own context written in.

## What it does

- **Actors** -- state and international actors (Serbia, Kosovo, USA, EU,
  Russia, China, NATO, UN, Albania, India, OSCE, ICJ) and their role in the
  dispute
- **Events** -- 10 milestones of the negotiations (1989-2023), with ZOPA,
  ripeness, BATNA, red lines, economic/military/social weights per event
- **Dashboard** -- 5 interactive charts built on the deterministic scores
  (ZOPA vs. implementation success, Power Index breakdown, Serbia's power
  transformation, political vs. economic cost, Window Score vs.
  implementation -- the central finding: conditions were ripe in 2013/2023,
  but implementation stayed low)
- **Synthesis / Compare / per-event Q&A** -- LLM interpretation (Anthropic
  Claude) over existing data, answering in the same language the question was
  asked in, with an explicit disclaimer on every answer

## Methodology

Every number on this platform that isn't raw seed data goes through the same
four-stage, fully deterministic pipeline (no LLM involvement, all in
`backend/app/services/analytics.py`):

1. **Normalize** -- each indicator (e.g. GDP growth of -10.33%) is rescaled to
   a common 0-100 range, with fixed min/max bounds per indicator type. For
   `unemployment_rate` the direction is inverted (a lower raw value produces
   a higher score). `GDP_absolute_usd` and `military_expenditure_usd` use a
   logarithmic scale instead of linear -- Serbia's economy and military
   budget are roughly an order of magnitude larger than Kosovo's, and a
   linear scale would flatten Kosovo into a near-constant low score
   regardless of real change.
2. **Category score** -- for each country/year, the normalized indicators in
   the same category (ECONOMIC, MILITARY, SOCIAL_UNREST) are averaged.
   ECONOMIC combines up to four indicators (GDP growth, GDP absolute size,
   unemployment, FDI net inflows); MILITARY combines two (military
   expenditure as % of GDP and in absolute USD); SOCIAL_UNREST is the
   Freedom House score alone.
3. **Power Index** (0-100, per country/year) -- the three category scores
   combined as Economic 40% + Military 40% + Social 20%.
4. **Window Score** (0-100, per year) -- estimates how ripe a given year was
   for agreement: power symmetry between Serbia and Kosovo (50%, `100 -
   Power Gap`) + mutual decline in power relative to the previous available
   year (30%, a Zartman "mutually hurting stalemate" signal) + social
   stability (20% -- higher domestic stability contributes positively; see
   Limitations for why).

**Data sources:** the 10 negotiation events and their qualitative fields
(ZOPA, ripeness, BATNA, red lines) come from my thesis, entered as seed data.
The quantitative indicators are a mix -- some read directly from thesis
charts, others pulled from the World Bank API (GDP, unemployment, military
expenditure, FDI) and Freedom House. Full source-by-source breakdown,
confidence levels, and every indicator I researched and rejected:
[SEED_SOURCE.md](SEED_SOURCE.md).

**The weight percentages (40/40/20, 50/30/20) are my own design, not an
empirical or cited result.** I looked at the Composite Index of National
Capability (CINC, Correlates of War project) as a point of reference -- the
closest established analogue, a similarly-composed national-power score --
but didn't adopt its methodology. CINC uses six unweighted, globally-
normalized components (population, urban population, steel production,
energy consumption, military spending, military personnel), built for
comparing states across the entire international system since 1816. Several
of those components are structurally meaningless for a young, small state
like Kosovo, and CINC's world-share normalization would flatten both
countries into a near-constant low score regardless of their real relative
dynamic -- the same distortion I found and fixed with linear GDP scaling.
My weights reflect my own judgment about what matters most in this
negotiation context, not a citable methodology. Full comparison:
[SEED_SOURCE.md §9](SEED_SOURCE.md).

## Limitations

The dataset has real, documented gaps -- I'd rather state them plainly than
hide them behind smooth-looking charts.

- **The full Power Index (Economic + Military + Social together) is only
  computable for four years: 2005, 2007, 2013, 2023.** Both countries need
  data in all three categories the same year, and Freedom House (the only
  Social indicator) only has values for odd years from 2005 onward. Years
  with partial data (e.g. 1998-2000, 2008, 2018, 2020) show up as explicit
  gaps in the dashboard charts, not zeroes.
- **Kosovo's pre-2008 economic/military data is sparse.** It wasn't tracked
  as a separate reporting entity by the World Bank before independence, and
  no Kosovo military body existed before the Kosovo Security Force (founded
  Jan 2009). Where that's encoded as `0.0` military spending, it's a
  documented historical fact, not an estimate filling a gap.
- **`troop_presence_index`** (foreign NATO/KFOR military presence in Kosovo)
  is stored as context but deliberately excluded from the Power Index -- it
  measures someone else's military footprint, not Kosovo's own capability.
- **No reliable, symmetric source for military capability beyond spending
  exists for this pair of countries.** I looked: IISS Military Balance is
  subscription-only, Global Firepower Index has documented, non-transparent
  methodology (multiple independent sources call it unreliable), SIPRI
  arms-transfer data is real but too sparse for Kosovo to be useful, and the
  Correlates of War capability dataset has no personnel data for Kosovo at
  all. Full research trail, including cross-checks against the CIA World
  Factbook: [SEED_SOURCE.md](SEED_SOURCE.md).
- **The weight percentages are my own design, not a citation** -- see
  Methodology above for the full explanation and the comparison with CINC.
- **Social stability, not instability, contributes positively to the Window
  Score.** An earlier version of this got the direction backwards, crediting
  *instability* as "pressure toward compromise." Per the thesis (Putnam's
  Two-Level Game, cited in [SEED_SOURCE.md §7](SEED_SOURCE.md)), domestic
  political instability narrows a leader's negotiating "win set" and raises
  the political cost of concessions, making agreement harder, not easier.
  Full rationale and a concrete example from the seed data:
  [SEED_SOURCE.md §10](SEED_SOURCE.md).

## Tech stack

**Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, Anthropic Claude API,
slowapi (rate limiting), pytest
**Frontend:** React, TypeScript, Vite, React Router, TanStack Query, Recharts

## Running it

### With Docker Compose (recommended -- one command, nothing else)

```bash
docker compose up --build
```

Brings up all 3 services (`db`, `api`, `frontend`) -- migrations and seed
data run automatically on first startup. Frontend: http://localhost:3000,
API: http://localhost:8000/docs (Swagger).

Needs a `backend/.env` -- copy `backend/.env.example` and fill in real
values (`DATABASE_URL`, `JWT_SECRET_KEY`, `ANTHROPIC_API_KEY`; see
`app/core/config.py` for the full list). `ADMIN_EMAIL`/`ADMIN_PASSWORD`
can stay blank locally -- the seed script falls back to a dev-only default
admin account with a warning, but I set them explicitly on the production
deployment (Railway) so the real site doesn't run on default credentials.

### Manually (without Docker, for development)

```bash
# DB only
docker compose up -d db

# Backend (from backend/)
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
alembic upgrade head
python -m app.scripts.seed
uvicorn main:app --reload                       # :8000

# Frontend (from frontend/, separate terminal)
npm install
npm run dev                                      # :5173
```

### Tests

```bash
cd backend
pytest -q                # 92 tests -- unit (mocked) + integration (test DB)
```

## Structure

```
backend/    FastAPI -- api/ (routers) → services/ (business logic) →
            repositories/ (DB queries) → models/ (SQLAlchemy)
frontend/   React -- pages/ (routes) → components/ (primitives, charts) →
            api/ (resource modules, one per backend entity)
```

Vertical-slice pattern for every new entity/feature: model → migration →
repository → service → schema → router → tests (backend), types → resource
module → hook/component → page (frontend).

## Documentation

Everything above is enough to understand the platform. These are supporting
documents, each written for a different purpose:

- [SEED_SOURCE.md](SEED_SOURCE.md) -- the full data-source breakdown, one
  entry per indicator and event: where every number comes from, its
  confidence level, and the complete research trail for indicators I
  considered and rejected (IISS, SIPRI arms transfers, CINC, Correlates of
  War, CIA World Factbook, and others). Read this to verify a specific
  figure.
- [PROJECT_STATUS.md](PROJECT_STATUS.md) -- a detailed, session-by-session
  development log, in Greek, written for my own reference while building
  this with an AI coding assistant. Not necessary reading for evaluating the
  project.
- [PROJECT_PLAN.md](PROJECT_PLAN.md) -- the original roadmap, at a
  milestone level, in Greek. Mostly historical at this point -- kept for
  context on how the project was originally scoped.
- [CLAUDE.md](CLAUDE.md) -- the instructions file I wrote for the AI coding
  agent: architecture rules, conventions, business rules, what not to do.
  In Greek. Documents how I structured the human-AI collaboration on this
  project, not something you need to read to evaluate the platform itself.
