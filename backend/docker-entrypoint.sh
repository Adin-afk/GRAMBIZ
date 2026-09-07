#!/bin/sh
set -e

echo "=== Solapur Rural Business Advisor - backend startup ==="

echo "[1/4] Waiting for database to be reachable..."
python -m app.utils.wait_for_db

echo "[2/4] Running Alembic migrations..."
python -m alembic upgrade head

if [ "${SEED_DEMO_DATA:-true}" = "true" ]; then
  echo "[3/4] Seeding demo data (skipped automatically if already present)..."
  python /app/scripts/seed_database.py
else
  echo "[3/4] SEED_DEMO_DATA=false - skipping demo data seed."
fi

echo "[4/4] Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
