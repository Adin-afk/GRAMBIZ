# PostgreSQL 16 + PostGIS 3 + pgvector, combined in one image.
#
# This is the exact same combination (postgresql-16-postgis-3 +
# postgresql-16-pgvector via apt) that was manually installed and verified
# working during development - see BUILD_STATUS.md.
FROM postgres:16

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-16-postgis-3 \
        postgresql-16-pgvector \
    && rm -rf /var/lib/apt/lists/*

# Enable both extensions automatically for every database created in this
# cluster (including the default one named by POSTGRES_DB). This runs once,
# the first time the data directory is initialized.
COPY init-extensions.sql /docker-entrypoint-initdb.d/01-init-extensions.sql
