#!/usr/bin/env bash
# Apply Postgres schema using DATABASE_URL (same DB the FastAPI app uses).
# Use when you see: relation "users" does not exist
#
# From repo root (with .env containing DATABASE_URL):
#   set -a && source .env && set +a && ./backend/database/postgres/scripts/apply-schema-env.sh
#
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set. Export it or: set -a && source .env && set +a" >&2
  exit 1
fi

# psql expects postgresql://… — strip SQLAlchemy async drivers (+asyncpg, +psycopg, etc.)
PSQL_URL=$(echo "$DATABASE_URL" | sed 's|^postgresql+[^:]*://|postgresql://|')

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PG_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Idempotent: full initial SQL cannot be re-run (ENUMs/tables already exist).
USERS_EXISTS="$(psql "$PSQL_URL" -tAc "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users');")"
if [[ "${USERS_EXISTS:-}" == "t" ]]; then
  echo "Initial schema already applied (public.users exists). Skipping 2026-04-01_initial_schema.sql."
else
  echo "Applying initial schema..."
  psql "$PSQL_URL" -v ON_ERROR_STOP=1 -f "$PG_ROOT/migrations/2026-04-01_initial_schema.sql"
fi

echo "Applying onboarding columns..."
psql "$PSQL_URL" -v ON_ERROR_STOP=1 -f "$PG_ROOT/migrations/2026-04-01_add_onboarding_to_profiles.sql"

echo "Running Alembic migrations..."
cd "$BACKEND_ROOT"
export DATABASE_URL
if [[ -x "./venv/bin/alembic" ]]; then
  ./venv/bin/alembic upgrade head
else
  alembic upgrade head
fi

echo "Done. PostgreSQL schema is up to date for this DATABASE_URL."
