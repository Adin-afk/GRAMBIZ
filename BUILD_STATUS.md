# Build Status - GramBiz

This is a work-in-progress build. This document is the honest source of
truth for what's actually implemented and tested vs. what's still to come.
Read this before README.md/SETUP.md (which describe the target end state).

## What's real and tested right now

- **Database**: full 44-table PostgreSQL schema (`backend/app/models/`),
  migrated via Alembic (`backend/alembic/versions/`), running against
  PostgreSQL 16 + PostGIS 3.4 + pgvector 0.6. GIST spatial indexes verified
  on `talukas`, `villages`, `businesses`, `markets`.
- **Seed data** (`scripts/seed_database.py`): Maharashtra -> Solapur -> the
  11 real talukas (public administrative fact, not a statistic). Everything
  below that - 46 villages, businesses, markets, prices, loan schemes - is
  **DEMO data**, explicitly marked `data_status = DEMO` in every row and in
  every API response. It is structurally realistic (right shape, right
  ranges) but **not verified real-world Solapur statistics**. Replace it via
  the CSV import pipeline once government datasets are available.
- **Backend API** (FastAPI, `backend/app/`): auth (register/login/JWT),
  location hierarchy, business categories, PostGIS-backed nearby-business
  and nearby-market queries, market price analysis, the deterministic
  financial engine (project cost / loan amount / EMI / full amortization
  schedule), loan scheme matching, the deterministic opportunity-scoring
  engine (DB-configurable weights, not hard-coded), the "what business
  should I start" recommendation endpoint, and the full assessment
  create/save/retrieve flow.
- **Tests**: 13 pytest unit tests on the financial engine and scoring
  service, all passing. Manually verified against a live server: the
  spec's own worked example (₹1L margin -> ₹10L project cost -> ₹9L loan),
  boundary conditions (₹0, negative, ₹1.4L, >₹50L), and the full
  location -> GIS -> scoring -> financial -> scheme-match -> save pipeline.
- **Frontend** (React + TypeScript + Vite + Tailwind v4, `frontend/`):
  login/register, dashboard, location selection (Maharashtra > Solapur >
  Taluka > Village, fetched from the API), the "what business should I
  start" ranked recommendation page with score breakdown, the financial
  calculator (project cost/loan/EMI/full repayment schedule), loan scheme
  cards, a Leaflet map with real PostGIS-backed nearby-business/market
  markers and 5/10km radius circles, and the saved-assessment report page.
  Every non-verified figure carries a visible VERIFIED/DEMO/UNVERIFIED
  badge. **Verified with actual browser screenshots** (Playwright) against
  the live backend - not just "it compiles": login, the full location to
  recommendation to saved-report flow, and the financial calculator all
  confirmed working end-to-end with real computed numbers on screen.

### How to run what exists

**Easiest: Docker Compose.** See `RUNNING_WITH_DOCKER.md` for full,
step-by-step instructions. Short version:

```bash
docker compose up --build
```

Then open http://localhost:5173. This starts PostgreSQL+PostGIS+pgvector,
runs migrations, seeds demo data (skipped automatically if data already
exists), and serves the frontend - all in one command. The startup
sequence (wait-for-db -> migrate -> seed -> serve) was verified end-to-end
against a real fresh PostgreSQL database; see the note at the top of
`RUNNING_WITH_DOCKER.md` for exactly what was and wasn't tested, since
Docker itself wasn't available in the build environment.

**Manual (no Docker):**

```bash
# 1. Postgres with PostGIS + pgvector must be running and reachable.

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL etc.
alembic upgrade head
cd ..
python scripts/seed_database.py
cd backend
uvicorn app.main:app --reload
# API docs at http://localhost:8000/docs
```

Demo login (seeded): `admin@solapur-rural-demo.com` / `demo@solapur-rural-demo.com`,
password `ChangeMe123!`.

```bash
# 3. Frontend (in a separate terminal, backend must be running)
cd frontend
npm install
cp .env.example .env   # point VITE_API_BASE_URL at your backend if not :8000
npm run dev
# App at http://localhost:5173
```

The full flow - login, location selection, "what business should I start",
financial calculator, map, and saved reports - has been verified working
end-to-end with real browser screenshots against a live backend, not just
checked for compile errors.

## Screenshots (from an actual working run)

See `docs/screenshots/` - these are real Playwright screenshots taken
against the live backend + seeded DEMO data during development, not mockups:
login, dashboard, location selection, business recommendation, saved
report, financial calculator, map, and loan schemes.

## What's NOT built yet

- **RAG pipeline / LLM advisory explanation**: `documents`/`document_chunks`
  tables exist and pgvector is enabled, but no ingestion pipeline or
  retrieval code has been written yet. `ai_explanation` fields are `null`.
- **ML training pipeline** (`app/ml/`): folder exists, empty. The current
  "opportunity score" is deterministic rule-based scoring, not a trained
  model - which is honest given there's no real historical outcome data to
  train on yet (per the spec's own transparency requirement).
- **Admin CSV import pipeline / admin dashboard UI**: not built.
- **i18n / Marathi & Hindi translation**: not wired up yet (English only).
- **Saved-assessments list page** ("my reports"): only direct-by-ID report
  viewing exists (`/reports/:id`); no listing page yet.
- **Windows .bat scripts, full README/SETUP.md, Docker packaging**: not
  written yet.

## Known rough edges

- `backend/.env` and `frontend/.env` are removed from this package - copy
  the `.env.example` files yourself and point them at your own Postgres
  instance / backend URL (only needed for the manual, non-Docker path -
  Docker Compose handles this automatically).
- Selected location/capital lives in React context only - resets on a hard
  page reload (not yet persisted to localStorage).
- Map tiles require internet access to `tile.openstreetmap.org` at
  runtime.
