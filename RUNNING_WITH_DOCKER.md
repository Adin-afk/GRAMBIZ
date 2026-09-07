# Running with Docker Compose

This is the easiest way to run the whole platform - one command starts
PostgreSQL+PostGIS+pgvector, the backend API, and the frontend, all wired
together, with the database automatically migrated and seeded with demo
data on first run.

**Honesty note:** this Docker Compose setup was written and carefully
checked (valid YAML, all Dockerfile COPY paths verified to exist, shell
script syntax checked, LF line endings enforced), and the exact startup
sequence it runs - wait for DB, run migrations, seed demo data, start the
API - was tested end-to-end against a real fresh PostgreSQL database
outside of Docker (see `BUILD_STATUS.md`). However, Docker itself was not
available in the environment this was built in, so `docker compose up`
has not been run as a whole. If something doesn't come up cleanly, check
the Troubleshooting section below first - the fix is very likely there.

## What you need installed

- **Docker Desktop** (Windows, Mac, or Linux). Get it from
  https://www.docker.com/products/docker-desktop/. On Windows, make sure
  WSL 2 is enabled (Docker Desktop will prompt you to install it if it's
  missing).
- That's it. You do **not** need Python, Node.js, or PostgreSQL installed
  on your laptop for this path - Docker handles all of it.

## Step 1: Get the project onto your laptop

Unzip the project folder anywhere convenient, e.g. `C:\projects\solapur-rural-business-advisor`
(Windows) or `~/projects/solapur-rural-business-advisor` (Mac/Linux).

## Step 2: Open a terminal in the project folder

- **Windows**: open the folder in File Explorer, then right-click inside
  it and choose "Open in Terminal" (or open PowerShell and `cd` to the
  folder).
- **Mac/Linux**: open Terminal and `cd` to the folder.

Confirm you're in the right place - this command should show
`docker-compose.yml` in the output:

```bash
ls
```

## Step 3 (optional): Configure ports/credentials

The defaults work out of the box. Only do this step if you want to change
something (e.g. port 8000 is already used by another app on your laptop).

```bash
cp .env.example .env
```

Then open `.env` in any text editor and change what you need. Common
reasons to edit it:
- `BACKEND_PORT` or `FRONTEND_PORT` already used by something else
- You want a real `JWT_SECRET` instead of the placeholder

## Step 4: Start everything

```bash
docker compose up --build
```

The first run will take a few minutes - it's building three images
(database, backend, frontend) and downloading their base layers. You'll
see interleaved logs from all three services. Watch for:

```
solapur_backend  | [4/4] Starting API server...
solapur_backend  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

That line means the backend is up, migrated, and seeded. Once you also see
nginx start in the `solapur_frontend` logs, everything is ready.

To run it in the background instead (so you get your terminal back):

```bash
docker compose up --build -d
```

## Step 5: Open the app

Go to **http://localhost:5173** in your browser.

Log in with the seeded demo account:
- Email: `demo@solapur-rural-demo.com`
- Password: `ChangeMe123!`

(There's also an admin account: `admin@solapur-rural-demo.com`, same
password.)

Backend API docs (Swagger UI) are at **http://localhost:8000/docs** if you
want to explore or test the API directly.

## Everyday commands

```bash
# Stop everything (keeps your data)
docker compose down

# Start again later (fast - no rebuild needed unless you changed code)
docker compose up -d

# Rebuild after you've changed backend or frontend code
docker compose up --build -d

# View logs
docker compose logs -f              # all services
docker compose logs -f backend      # just the backend
docker compose logs -f frontend
docker compose logs -f db

# Check what's running
docker compose ps

# Stop everything AND delete the database (start completely fresh)
docker compose down -v
```

## How the pieces fit together

```
Your browser (http://localhost:5173)
        |
        v
  frontend container (nginx serving the built React app, port 80 -> 5173)
        |
        | REST calls to http://localhost:8000 (your laptop, not the Docker network)
        v
  backend container (FastAPI, port 8000 -> 8000)
        |
        | DATABASE_URL points at the "db" service by its container name
        v
  db container (PostgreSQL 16 + PostGIS + pgvector, port 5432 -> 5432)
```

A subtlety worth understanding: the **frontend talks to the backend from
your browser**, not from inside the Docker network - so its API base URL
is `http://localhost:8000`, a real address on your laptop. The **backend
talks to the database from inside the Docker network**, so its
`DATABASE_URL` uses the service name `db`, not `localhost`. This is why
`VITE_API_BASE_URL` and `DATABASE_URL` look different in
`docker-compose.yml` even though they're both "how do I reach the other
service."

## What happens automatically on first start

1. The `db` service builds a PostgreSQL 16 image with PostGIS and pgvector
   installed, and creates both extensions on first boot.
2. The `backend` service waits for the database to accept connections,
   then runs `alembic upgrade head` (creates all 44 tables), then seeds
   demo data (46 DEMO-labeled villages across the 11 real Solapur talukas,
   demo businesses/markets/prices/loan schemes) - **but only if the
   database is empty**. Restarting the stack later will detect existing
   data and skip re-seeding automatically.
3. The `frontend` service builds the production React bundle and serves
   it via nginx.

Your database data persists in a Docker volume (`solapur_postgres_data`)
across `docker compose down` / `docker compose up` cycles. It's only
deleted if you explicitly run `docker compose down -v`.

## Troubleshooting

**"Cannot connect to the Docker daemon"** - Docker Desktop isn't running.
Start it and wait for the whale icon to say it's ready, then retry.

**Port already in use (5432 / 8000 / 5173)** - something else on your
laptop is using that port. Copy `.env.example` to `.env` and change
`POSTGRES_PORT`, `BACKEND_PORT`, or `FRONTEND_PORT` to a free port (e.g.
`FRONTEND_PORT=5174`), then `docker compose up --build -d` again. If you
change `BACKEND_PORT`, also update `VITE_API_BASE_URL` in `.env` to match,
since the frontend needs to know the new port.

**Backend keeps restarting / never becomes healthy** - check its logs:
```bash
docker compose logs backend
```
If it's stuck waiting for the database, give it a minute - Postgres can
take longer to initialize on the very first run (creating the data
directory). If it's an actual migration error, that's a real bug - please
report it with the log output.

**Frontend loads but shows network/CORS errors** - double check
`VITE_API_BASE_URL` in `.env` matches `BACKEND_PORT`. Remember the
frontend was *built* with that URL baked in, so after changing it you
need to rebuild: `docker compose up --build -d`.

**"exec format error" or `$'\r': command not found` on
`docker-entrypoint.sh`** - this means the shell script got Windows-style
line endings somewhere along the way (e.g. an editor auto-converted it).
The `.gitattributes` file in this repo prevents that if you're using git;
if you edited the file directly on Windows, re-save it with LF line
endings (most editors have a "line ending" setting in the status bar).

**Map tiles don't load** - the map needs internet access to
`tile.openstreetmap.org` at runtime (this is normal for Leaflet + OSM and
has nothing to do with Docker).

**I want to start completely fresh** (wipe the database and reseed):
```bash
docker compose down -v
docker compose up --build -d
```

**I want to see the database directly** (e.g. with a GUI tool like
pgAdmin or TablePlus): connect to `localhost:5432` (or your custom
`POSTGRES_PORT`) with the credentials from `.env` (defaults:
`solapur_user` / `solapur_pass` / database `solapur_rural_db`).
