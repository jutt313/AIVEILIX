#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN_DIR="$ROOT/run"
PORT="5433"
DB_NAME="aiveilix"
DB_USER="postgres"
SCHEMA_FILE="$ROOT/migrations/2026-04-01_initial_schema.sql"

createdb -h "$RUN_DIR" -p "$PORT" -U "$DB_USER" "$DB_NAME" 2>/dev/null || true
psql -h "$RUN_DIR" -p "$PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCHEMA_FILE"

echo "Schema applied to database: $DB_NAME"
