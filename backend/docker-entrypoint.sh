#!/bin/sh
# set -e: σταματάει αμέσως αν το alembic upgrade αποτύχει -- καλύτερα να
# μη σηκωθεί καθόλου το API παρά να τρέξει πάνω σε λάθος/μισό schema.
set -e

echo "[entrypoint] Running migrations..."
alembic upgrade head

echo "[entrypoint] Seeding (idempotent -- skips if data already present)..."
python -m app.scripts.seed

echo "[entrypoint] Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
