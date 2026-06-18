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
if [ ! -f "$RUNTIME_ENV" ]; then
  echo "Missing $RUNTIME_ENV. Run deploy/gcp/provision.sh first." >&2
  exit 1
fi

set -a
source "$CONFIG_FILE"
source "$RUNTIME_ENV"
set +a

gcloud config set project "$PROJECT_ID" >/dev/null

IMAGE="${BACKEND_IMAGE:-$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/$BACKEND_SERVICE:$(date +%Y%m%d%H%M%S)}"
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
RUN_SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:$RUN_SERVICE_ACCOUNT" \
  --role roles/secretmanager.secretAccessor \
  --condition=None \
  --quiet >/dev/null
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:$RUN_SERVICE_ACCOUNT" \
  --role roles/cloudsql.client \
  --condition=None \
  --quiet >/dev/null

if [ -n "${BACKEND_IMAGE:-}" ]; then
  echo "Using existing backend image: $IMAGE"
else
  echo "Building backend image..."
  gcloud builds submit "$REPO_ROOT/backend" --tag "$IMAGE" --quiet
fi

"$SCRIPT_DIR/sync-secrets.sh"
SECRETS_ARG="$(cat "$REPO_ROOT/.gcloud/cloudrun-set-secrets.txt")"

MIGRATE_JOB="${BACKEND_SERVICE}-migrate"
echo "Deploying migration job..."
gcloud run jobs deploy "$MIGRATE_JOB" \
  --image "$IMAGE" \
  --region "$REGION" \
  --set-env-vars APP_ENV=production \
  --set-secrets "$SECRETS_ARG" \
  --set-cloudsql-instances "$CLOUDSQL_CONNECTION_NAME" \
  --vpc-connector "$VPC_CONNECTOR" \
  --vpc-egress private-ranges-only \
  --command python \
  --args scripts/apply_schema.py \
  --task-timeout 600 \
  --max-retries 0 \
  --labels "$LABELS" \
  --quiet

echo "Running migrations..."
gcloud run jobs execute "$MIGRATE_JOB" --region "$REGION" --wait --quiet

echo "Deploying backend service with cost caps..."
gcloud run deploy "$BACKEND_SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --allow-unauthenticated \
  --ingress all \
  --set-env-vars APP_ENV=production \
  --set-secrets "$SECRETS_ARG" \
  --set-cloudsql-instances "$CLOUDSQL_CONNECTION_NAME" \
  --vpc-connector "$VPC_CONNECTOR" \
  --vpc-egress private-ranges-only \
  --cpu "$CLOUD_RUN_CPU" \
  --memory "$CLOUD_RUN_MEMORY" \
  --concurrency "$CLOUD_RUN_CONCURRENCY" \
  --timeout "$CLOUD_RUN_TIMEOUT" \
  --min-instances "$CLOUD_RUN_MIN_INSTANCES" \
  --max-instances "$CLOUD_RUN_MAX_INSTANCES" \
  --labels "$LABELS" \
  --quiet

SERVICE_URL="$(gcloud run services describe "$BACKEND_SERVICE" --region "$REGION" --format='value(status.url)')"

python3 - "$RUNTIME_ENV" "$SERVICE_URL" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
service_url = sys.argv[2].rstrip("/")
lines = path.read_text().splitlines()
out = []
seen_api = seen_mcp = False
for line in lines:
    if line.startswith("MCP_BASE_URL="):
        out.append(f"MCP_BASE_URL={service_url}")
        seen_mcp = True
    else:
        out.append(line)
if not seen_mcp:
    out.append(f"MCP_BASE_URL={service_url}")
path.write_text("\n".join(out) + "\n")
PY

"$SCRIPT_DIR/sync-secrets.sh"
gcloud run services update "$BACKEND_SERVICE" \
  --region "$REGION" \
  --update-secrets MCP_BASE_URL=MCP_BASE_URL:latest \
  --quiet >/dev/null

echo "Backend URL: $SERVICE_URL"
echo "MCP base URL set to backend URL for now. Custom mcp domain can be added later."
