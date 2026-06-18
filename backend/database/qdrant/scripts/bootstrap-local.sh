#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV="$ROOT/.venv"
SCRIPT="$ROOT/qdrant/bootstrap_collections.py"

"$VENV/bin/python" "$SCRIPT" --mode local
