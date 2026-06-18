#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV="$ROOT/.venv"
export QDRANT_LOCAL_PATH="$ROOT/qdrant/data/local"

"$VENV/bin/python" - <<'PY'
import os
from qdrant_client import QdrantClient

client = QdrantClient(path=os.environ["QDRANT_LOCAL_PATH"])

try:
    print("Collections:")
    for collection in client.get_collections().collections:
        info = client.get_collection(collection.name)
        print(f"- {collection.name}: points={info.points_count}")
finally:
    client.close()
PY
