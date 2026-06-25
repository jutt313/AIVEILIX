#!/usr/bin/env bash
# Phase 3 — provision the dedicated file-processing worker.
#
# Run this AFTER deploy-backend.sh. It:
#   1. creates the Cloud Tasks queue (idempotent)
#   2. ensures a PROCESSING_SECRET exists in Secret Manager
#   3. deploys a worker Cloud Run service from the API's current image, with
#      concurrency=1 + CPU always allocated so each instance fully processes one
#      file at a time and the service scales out horizontally per file
#   4. wires the API service to enqueue one Cloud Task per uploaded file
#
# Re-running is safe. To turn the worker OFF again, clear PROCESSING_QUEUE /
# PROCESSING_WORKER_URL on the API service and the API falls back to in-process.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/config.env}"
RUNTIME_ENV="$REPO_ROOT/.gcloud/prod-runtime.env"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Missing $CONFIG_FILE. Copy deploy/gcp/config.env.example first." >&2
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

WORKER_SERVICE="${WORKER_SERVICE:-${BACKEND_SERVICE}-worker}"
PROCESSING_QUEUE="${PROCESSING_QUEUE:-file-processing}"

gcloud config set project "$PROJECT_ID" >/dev/null
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
RUN_SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# 1. Cloud Tasks queue ────────────────────────────────────────────────────────
echo "Ensuring Cloud Tasks queue '$PROCESSING_QUEUE' exists in $REGION..."
if ! gcloud tasks queues describe "$PROCESSING_QUEUE" --location "$REGION" >/dev/null 2>&1; then
  gcloud tasks queues create "$PROCESSING_QUEUE" --location "$REGION" --quiet
fi
# Let the API's runtime SA enqueue tasks.
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:$RUN_SERVICE_ACCOUNT" \
  --role roles/cloudtasks.enqueuer \
  --condition=None --quiet >/dev/null

# 2. Shared secret in Secret Manager ───────────────────────────────────────────
if ! gcloud secrets describe PROCESSING_SECRET >/dev/null 2>&1; then
  echo "Creating PROCESSING_SECRET..."
  gcloud secrets create PROCESSING_SECRET --replication-policy=automatic --quiet
  python3 -c "import secrets; print(secrets.token_urlsafe(32))" \
    | gcloud secrets versions add PROCESSING_SECRET --data-file=- --quiet
fi
gcloud secrets add-iam-policy-binding PROCESSING_SECRET \
  --member "serviceAccount:$RUN_SERVICE_ACCOUNT" \
  --role roles/secretmanager.secretAccessor --quiet >/dev/null

# 3. Deploy the worker from the API's current image ─────────────────────────────
IMAGE="$(gcloud run services describe "$BACKEND_SERVICE" --region "$REGION" \
  --format='value(spec.template.spec.containers[0].image)')"
if [ -z "$IMAGE" ]; then
  echo "Could not resolve API image. Deploy the backend first." >&2
  exit 1
fi
echo "Deploying worker '$WORKER_SERVICE' from $IMAGE..."

"$SCRIPT_DIR/sync-secrets.sh"
SECRETS_ARG="$(cat "$REPO_ROOT/.gcloud/cloudrun-set-secrets.txt")"

gcloud run deploy "$WORKER_SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --allow-unauthenticated \
  --ingress all \
  --set-env-vars APP_ENV=production \
  --set-secrets "$SECRETS_ARG,PROCESSING_SECRET=PROCESSING_SECRET:latest" \
  --set-cloudsql-instances "$CLOUDSQL_CONNECTION_NAME" \
  --vpc-connector "$VPC_CONNECTOR" \
  --vpc-egress private-ranges-only \
  --cpu "${WORKER_CPU:-2}" \
  --memory "${WORKER_MEMORY:-4Gi}" \
  --concurrency 1 \
  --no-cpu-throttling \
  --timeout "${WORKER_TIMEOUT:-900}" \
  --min-instances 0 \
  --max-instances "${WORKER_MAX_INSTANCES:-10}" \
  --labels "$LABELS" \
  --quiet

WORKER_URL="$(gcloud run services describe "$WORKER_SERVICE" --region "$REGION" --format='value(status.url)')"
echo "Worker URL: $WORKER_URL"

# 4. Point the API at the queue + worker ────────────────────────────────────────
echo "Wiring API service '$BACKEND_SERVICE' to the worker..."
gcloud run services update "$BACKEND_SERVICE" \
  --region "$REGION" \
  --update-env-vars "PROCESSING_QUEUE=$PROCESSING_QUEUE,PROCESSING_WORKER_URL=$WORKER_URL,GCP_PROJECT=$PROJECT_ID,GCP_REGION=$REGION" \
  --update-secrets "PROCESSING_SECRET=PROCESSING_SECRET:latest" \
  --quiet >/dev/null

echo "Done. Uploads now enqueue one Cloud Task per file to: $WORKER_URL/v1/internal/process-file"
