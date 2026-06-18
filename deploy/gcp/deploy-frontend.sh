#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/config.env}"
RUNTIME_ENV="$REPO_ROOT/.gcloud/prod-runtime.env"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Missing $CONFIG_FILE. Copy deploy/gcp/config.env.example to deploy/gcp/config.env first." >&2
  exit 1
fi

set -a
source "$CONFIG_FILE"
if [ -f "$RUNTIME_ENV" ]; then
  source "$RUNTIME_ENV"
fi
set +a

gcloud config set project "$PROJECT_ID" >/dev/null

API_URL="${API_URL:-}"
if [ -z "$API_URL" ]; then
  API_URL="$(gcloud run services describe "$BACKEND_SERVICE" --region "$REGION" --format='value(status.url)' 2>/dev/null || true)"
fi
if [ -z "$API_URL" ]; then
  echo "Could not resolve backend API URL. Deploy backend first or pass API_URL=https://..." >&2
  exit 1
fi

echo "Building frontend against API: $API_URL"
(
  cd "$REPO_ROOT/frontend"
  VITE_API_URL="$API_URL" npm run build
)

firebase deploy --project "$PROJECT_ID" --only hosting

echo "Frontend deployed. Default URL should be: $FRONTEND_URL"
