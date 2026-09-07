"""
Blocks until the configured DATABASE_URL is reachable, or exits with an
error after a timeout. Used by the Docker entrypoint so the backend
container doesn't crash-loop while Postgres is still starting up.

Run directly:  python -m app.utils.wait_for_db
"""
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from app.config import get_settings


def wait_for_db(max_attempts: int = 30, delay_seconds: float = 2.0) -> None:
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"Database reachable after {attempt} attempt(s).")
            return
        except OperationalError as exc:
            print(f"[{attempt}/{max_attempts}] Database not ready yet ({exc.__class__.__name__}); retrying...")
            time.sleep(delay_seconds)

    print(f"ERROR: database not reachable after {max_attempts} attempts. Giving up.")
    sys.exit(1)


if __name__ == "__main__":
    wait_for_db()
