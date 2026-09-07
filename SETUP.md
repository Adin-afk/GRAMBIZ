# Setup Guide

Beginner-friendly, step-by-step. Two paths: **Docker (recommended, easiest)**
or **manual** (native Python/Node/Postgres, no Docker).

---

## Path A: Docker (recommended)

This is the easiest path and the one we recommend, especially on Windows.

### What to install

1. **Docker Desktop** — https://www.docker.com/products/docker-desktop/
   - Windows: the installer will prompt you to enable WSL 2 if it isn't
     already. Accept and let it install; restart if asked.
   - Mac/Linux: default install options are fine.
2. Nothing else. Docker handles Python, Node.js, and PostgreSQL for you.

### Steps

1. Unzip this project anywhere on your laptop.
2. Open a terminal (PowerShell on Windows, Terminal on Mac/Linux) and `cd`
   into the unzipped folder.
3. Run:
   ```bash
   docker compose up --build
   ```
4. Wait for the logs to show `Uvicorn running on http://0.0.0.0:8000`.
5. Open **http://localhost:5173** in your browser.
6. Log in: `demo@solapur-rural-demo.com` / `ChangeMe123!`.

That's it. For day-to-day commands (stopping, restarting, viewing logs,
resetting the database) and troubleshooting, see **`RUNNING_WITH_DOCKER.md`**.

---

## Path B: Manual (no Docker)

Use this if you want to run the backend or frontend natively - e.g. for
active development with hot-reload, or if you can't use Docker.

### What to install

- **Python 3.12** — https://www.python.org/downloads/ (check "Add to PATH"
  on the Windows installer)
- **Node.js 20+** — https://nodejs.org/
- **PostgreSQL 16 with PostGIS and pgvector extensions.** This is the
  fiddly part on native Windows - installing PostGIS and pgvector
  alongside Postgres from scratch is non-trivial. Two options:
  - **Easiest**: run just the `db` service from Docker Compose (it already
    has PostGIS + pgvector preinstalled) and point your native backend at
    it: `docker compose up db` then use `DATABASE_URL=postgresql+psycopg2://solapur_user:solapur_pass@localhost:5432/solapur_rural_db`.
  - **Fully native**: install PostgreSQL 16 via the official installer,
    then add the PostGIS and pgvector extensions via
    [Stack Builder](https://www.postgresql.org/download/windows/) (bundled
    with the Windows installer) or your package manager on Mac/Linux.
- **Git** (optional, if you're cloning rather than unzipping) —
  https://git-scm.com/downloads
- **VS Code** (optional but recommended) — https://code.visualstudio.com/

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
copy .env.example .env          # Windows: copy   Mac/Linux: cp
# edit .env if your DATABASE_URL differs from the default
alembic upgrade head
cd ..
python scripts/seed_database.py
cd backend
uvicorn app.main:app --reload
```

API is now at http://localhost:8000, docs at http://localhost:8000/docs.

### Frontend

In a **new** terminal:

```powershell
cd frontend
npm install
copy .env.example .env          # Windows: copy   Mac/Linux: cp
npm run dev
```

App is now at http://localhost:5173.

### PowerShell commands reference

| Task | Command |
|---|---|
| Create venv | `python -m venv .venv` |
| Activate venv | `.venv\Scripts\activate` |
| Install backend deps | `pip install -r requirements.txt` |
| Run migrations | `alembic upgrade head` |
| Seed demo data | `python scripts/seed_database.py` |
| Start backend | `uvicorn app.main:app --reload` |
| Install frontend deps | `npm install` |
| Start frontend | `npm run dev` |

### Command Prompt (cmd.exe) equivalents

Same as above, except venv activation is `.venv\Scripts\activate.bat`
instead of `.venv\Scripts\activate`.

---

## Which path should I use?

- **Just want to see it running / demo it**: Path A (Docker).
- **Actively editing backend or frontend code**: Path B gives faster
  reload cycles, but Path A works too if you don't mind rebuilding
  (`docker compose up --build`) after changes.
- **On Windows and unsure**: Path A. Getting PostGIS + pgvector working
  natively on Windows is genuinely fiddly; Docker sidesteps it entirely.
