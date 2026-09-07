# GramBiz Platform

AI-Driven Hyper-Local Business Advisory and Financial Structuring
Assistant for Rural Micro-Entrepreneurs — built for the SIH 2026 problem
statement, scoped initially to **Maharashtra → Solapur District → Rural
Areas**.

For a rural entrepreneur in Solapur district, given their village and
available capital, this platform determines which supported business
opportunities are most viable based on local data, geographic market
conditions, competition, financial feasibility, and applicable government
loan schemes — with every number traceable to a source and every
financial calculation deterministic (never LLM-generated).

**Read `BUILD_STATUS.md` before anything else.** It's the honest,
up-to-date account of exactly what's implemented, tested, and verified
right now versus what's still planned — this README describes the target
system, BUILD_STATUS.md describes the current one.

## Quick start

```bash
docker compose up --build
```

Then open **http://localhost:5173** and log in with
`demo@solapur-rural-demo.com` / `ChangeMe123!`.

Full step-by-step instructions, troubleshooting, and an explanation of how
the three services talk to each other: see **`RUNNING_WITH_DOCKER.md`**.

## Architecture

```
Maharashtra → Solapur District → Taluka → Village → Gram Panchayat
                                              ↓
                          Businesses / Markets / Infrastructure /
                          Population / Agriculture / Livestock data
                                              ↓
                    PostGIS spatial queries (5km / 10km analysis)
                                              ↓
              Deterministic opportunity scoring (DB-configurable weights)
                                              ↓
              Deterministic financial engine (project cost / loan / EMI)
                                              ↓
                       Loan scheme matching (DB-stored, versioned)
                                              ↓
                  RAG + LLM explanation (optional - app works without it)
                                              ↓
                          Saved AI Advisory Report
```

Three services, connected end-to-end:

- **`database/`** — PostgreSQL 16 + PostGIS + pgvector, 44-table schema,
  managed by Alembic migrations in `backend/alembic/`.
- **`backend/`** — FastAPI. Auth, location hierarchy, PostGIS-backed
  spatial queries, the deterministic financial engine, deterministic
  opportunity scoring, loan scheme matching, and the full assessment
  create/save/retrieve flow. Talks to `database` over the Docker network
  (`DATABASE_URL` points at the `db` service).
- **`frontend/`** — React + TypeScript + Vite + Tailwind. Login, location
  selection, "what business should I start", financial calculator, loan
  schemes, map, saved reports. Talks to `backend` over HTTP from the
  browser (`VITE_API_BASE_URL`, baked in at build time).

## Technology stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS v4, React Router,
  Axios, Leaflet
- **Backend**: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, JWT auth
- **Database**: PostgreSQL + PostGIS (spatial queries) + pgvector (RAG
  embeddings, not yet populated - see BUILD_STATUS.md)
- **Deployment**: Docker Compose (see `docker-compose.yml`,
  `RUNNING_WITH_DOCKER.md`)

## Folder structure

```
solapur-rural-business-advisor/
├── frontend/            React app (Dockerfile, nginx.conf included)
├── backend/              FastAPI app (Dockerfile, Alembic migrations, tests)
├── database/             Postgres+PostGIS+pgvector image definition
├── data/                 raw/processed/validated/training data folders
├── models/               production/archived ML model artifacts (empty - no ML trained yet)
├── scripts/               seed_database.py and future data-processing scripts
├── docs/                  screenshots + reference docs
├── tests/                  (top-level integration test placeholder; unit tests live in backend/tests)
├── docker-compose.yml
├── .env.example
├── BUILD_STATUS.md        <- read this first
├── RUNNING_WITH_DOCKER.md
└── SETUP.md
```

## Data provenance and honesty policy

Villages, businesses, market prices, and loan scheme terms currently
seeded in this project are **DEMO data** — structurally realistic but not
verified real-world Solapur statistics — and every such record is
explicitly tagged `data_status: DEMO` in the database and surfaced as a
visible badge in the UI. The 11 Solapur taluka names are the one exception:
those are public administrative facts, not statistics. Replace the DEMO
data via the CSV import pipeline once verified government datasets are
available (import pipeline not yet built - see BUILD_STATUS.md).

## Windows setup

Docker Desktop is the only prerequisite for the Docker Compose path (see
`SETUP.md` / `RUNNING_WITH_DOCKER.md`). If you want to run the backend or
frontend natively on Windows without Docker, see the manual setup section
in `BUILD_STATUS.md` — you'll need Python 3.12, Node.js, and a local
PostgreSQL+PostGIS+pgvector instance.
