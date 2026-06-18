#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$ROOT/data"

if [ -f "$DATA_DIR/PG_VERSION" ]; then
  pg_ctl -D "$DATA_DIR" stop
fi
