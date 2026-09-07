-- Runs once, automatically, the first time the Postgres data volume is
-- initialized (see /docker-entrypoint-initdb.d in the official Postgres
-- image docs). The Alembic migration also has an idempotent
-- CREATE EXTENSION IF NOT EXISTS for both, so this is a belt-and-braces
-- step that makes the extensions available immediately, even before
-- migrations run.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
