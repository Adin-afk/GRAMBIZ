FROM python:3.12-slim

# libpq-dev + gcc are needed to build psycopg2 from source if a prebuilt
# wheel isn't available for the target platform; curl is used by the
# healthcheck in docker-compose.yml.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/
COPY scripts/seed_database.py /app/scripts/seed_database.py

RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
