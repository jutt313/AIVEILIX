#!/bin/zsh
set -euo pipefail

PID_FILE="$(cd "$(dirname "$0")/.." && pwd)/run/valkey.pid"
PORT=6380

CLI_BIN=""
if command -v valkey-cli >/dev/null 2>&1; then
  CLI_BIN="valkey-cli"
elif command -v redis-cli >/dev/null 2>&1; then
  CLI_BIN="redis-cli"
fi

if [ -n "$CLI_BIN" ]; then
  "$CLI_BIN" -p "$PORT" shutdown nosave >/dev/null 2>&1 || true
fi

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
    kill "$PID"
  fi
  rm -f "$PID_FILE"
fi
