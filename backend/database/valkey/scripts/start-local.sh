#!/bin/zsh
set -euo pipefail

VALKEY_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$VALKEY_ROOT"

mkdir -p "$VALKEY_ROOT/data" "$VALKEY_ROOT/run" "$VALKEY_ROOT/logs"

PID_FILE="$VALKEY_ROOT/run/valkey.pid"
if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$PID" ] && ! kill -0 "$PID" >/dev/null 2>&1; then
    rm -f "$PID_FILE"
  fi
fi

if command -v valkey-server >/dev/null 2>&1; then
  valkey-server ./valkey.conf \
    --dir "$VALKEY_ROOT/data" \
    --pidfile "$VALKEY_ROOT/run/valkey.pid" \
    --logfile "$VALKEY_ROOT/logs/valkey.log"
  echo "Valkey started on port 6380"
elif command -v redis-server >/dev/null 2>&1; then
  redis-server ./valkey.conf \
    --dir "$VALKEY_ROOT/data" \
    --pidfile "$VALKEY_ROOT/run/valkey.pid" \
    --logfile "$VALKEY_ROOT/logs/valkey.log"
  echo "Compatible local server started on port 6380 (target architecture: Valkey)"
else
  echo "No valkey-server or redis-server binary found." >&2
  exit 1
fi
