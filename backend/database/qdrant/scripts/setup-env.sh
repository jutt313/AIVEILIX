#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV="$ROOT/.venv"
REQ_FILE="$ROOT/qdrant/requirements.txt"

if [ ! -d "$VENV" ]; then
  uv venv "$VENV"
fi

uv pip install --python "$VENV/bin/python" -r "$REQ_FILE"

echo "Qdrant environment ready at $VENV"
