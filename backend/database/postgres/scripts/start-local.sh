#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$ROOT/data"
RUN_DIR="$ROOT/run"
LOG_FILE="$ROOT/logs/postgres.log"
PORT="5433"

mkdir -p "$RUN_DIR" "$(dirname "$LOG_FILE")"

if [ ! -f "$DATA_DIR/PG_VERSION" ]; then
  rm -rf "$DATA_DIR"
  initdb -D "$DATA_DIR" --username=postgres --auth=trust >/dev/null
fi

pg_ctl -D "$DATA_DIR" -l "$LOG_FILE" -o "-k $RUN_DIR -p $PORT -c shared_memory_type=mmap -c dynamic_shared_memory_type=mmap" start

echo "PostgreSQL started on port $PORT"
echo "Socket dir: $RUN_DIR"
