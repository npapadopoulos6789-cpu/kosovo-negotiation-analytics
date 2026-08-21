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
  Claude) over existing data, with an explicit disclaimer on every answer

## The golden rule: separation of data sources

| Data | Source |
|---|---|
| Historical/economic/military/social | The thesis -- manually entered seed data |
| Power Index / Window Score / Optimal Periods | Our own code, deterministic computation, NOT the LLM |
| Interpretation (Synthesis/Compare/Q&A) | LLM over existing data -- never a source of new facts/figures |

Full source breakdown per indicator: [SEED_SOURCE.md](SEED_SOURCE.md).

## Tech stack

**Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, Anthropic Claude API, pytest
**Frontend:** React, TypeScript, Vite, React Router, TanStack Query, Recharts

## Running it

### With Docker Compose (recommended -- one command, nothing else)

```bash
docker compose up --build
```

Brings up all 3 services (`db`, `api`, `frontend`) -- migrations and seed
data run automatically on first startup. Frontend: http://localhost:3000,
API: http://localhost:8000/docs (Swagger).

Needs a `backend/.env` with `DATABASE_URL`, `JWT_SECRET_KEY`,
`ANTHROPIC_API_KEY` (see the variable names in `app/core/config.py`).

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
pytest -q                # 87 tests -- unit (mocked) + integration (test DB)
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

- [SEED_SOURCE.md](SEED_SOURCE.md) -- full data-source breakdown per indicator/event
- [PROJECT_STATUS.md](PROJECT_STATUS.md) -- detailed session-by-session log (agent-facing, in Greek)
- [PROJECT_PLAN.md](PROJECT_PLAN.md) -- original roadmap, milestone-level (in Greek)
- [CLAUDE.md](CLAUDE.md) -- instructions for the AI coding agent: architecture rules, conventions (in Greek)
