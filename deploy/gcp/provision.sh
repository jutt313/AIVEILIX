#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/config.env}"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Missing $CONFIG_FILE. Copy deploy/gcp/config.env.example to deploy/gcp/config.env first." >&2
  exit 1
fi

set -a
source "$CONFIG_FILE"
set +a

gcloud config set project "$PROJECT_ID"

echo "Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  vpcaccess.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  servicenetworking.googleapis.com

if ! gcloud artifacts repositories describe "$ARTIFACT_REPO" --location "$REGION" >/dev/null 2>&1; then
  gcloud artifacts repositories create "$ARTIFACT_REPO" \
    --repository-format=docker \
    --location="$REGION" \
    --description="AIveilix containers" \
    --labels="$LABELS"
fi

if ! gcloud compute networks vpc-access connectors describe "$VPC_CONNECTOR" --region "$REGION" >/dev/null 2>&1; then
  gcloud compute networks vpc-access connectors create "$VPC_CONNECTOR" \
    --region "$REGION" \
    --range "$VPC_CONNECTOR_RANGE" \
    --min-instances 2 \
    --max-instances 3 \
    --machine-type e2-micro
fi

if ! gcloud compute disks describe "${VM_NAME}-data" --zone "$ZONE" >/dev/null 2>&1; then
  gcloud compute disks create "${VM_NAME}-data" \
    --zone "$ZONE" \
    --size "$VM_DATA_DISK_SIZE" \
    --type "$VM_DATA_DISK_TYPE" \
    --labels="$LABELS"
fi

if ! gcloud compute instances describe "$VM_NAME" --zone "$ZONE" >/dev/null 2>&1; then
  gcloud compute instances create "$VM_NAME" \
    --zone "$ZONE" \
    --machine-type "$VM_MACHINE_TYPE" \
    --image-family debian-12 \
    --image-project debian-cloud \
    --boot-disk-size "$VM_BOOT_DISK_SIZE" \
    --disk "name=${VM_NAME}-data,device-name=aiveilix-data,mode=rw,boot=no,auto-delete=no" \
    --metadata-from-file "startup-script=$SCRIPT_DIR/vm-startup.sh" \
    --tags aiveilix-internal \
    --labels="$LABELS"
fi

if ! gcloud compute firewall-rules describe aiveilix-vector-cache-from-connector >/dev/null 2>&1; then
  gcloud compute firewall-rules create aiveilix-vector-cache-from-connector \
    --network default \
    --direction INGRESS \
    --priority 1000 \
    --source-ranges "$VPC_CONNECTOR_RANGE" \
    --target-tags aiveilix-internal \
    --allow tcp:6333,tcp:6379
fi

if ! gcloud sql instances describe "$SQL_INSTANCE" >/dev/null 2>&1; then
  gcloud sql instances create "$SQL_INSTANCE" \
    --database-version "$SQL_VERSION" \
    --region "$REGION" \
    --edition enterprise \
    --cpu "$SQL_CPU" \
    --memory "$SQL_MEMORY" \
    --storage-type SSD \
    --storage-size "$SQL_STORAGE_SIZE" \
    --no-storage-auto-increase \
    --availability-type ZONAL \
    --backup-start-time 09:00
  gcloud sql instances patch "$SQL_INSTANCE" \
    --update-labels="$LABELS" \
    --quiet >/dev/null || true
fi

if ! gcloud sql databases describe "$SQL_DATABASE" --instance "$SQL_INSTANCE" >/dev/null 2>&1; then
  gcloud sql databases create "$SQL_DATABASE" --instance "$SQL_INSTANCE"
fi

mkdir -p "$REPO_ROOT/.gcloud"
if [ ! -f "$REPO_ROOT/.gcloud/sql-password" ]; then
  openssl rand -base64 36 > "$REPO_ROOT/.gcloud/sql-password"
  chmod 600 "$REPO_ROOT/.gcloud/sql-password"
fi
SQL_PASSWORD="$(cat "$REPO_ROOT/.gcloud/sql-password")"
gcloud sql users create "$SQL_USER" \
  --instance "$SQL_INSTANCE" \
  --password "$SQL_PASSWORD" >/dev/null 2>&1 || \
gcloud sql users set-password "$SQL_USER" \
  --instance "$SQL_INSTANCE" \
  --password "$SQL_PASSWORD"

VM_PRIVATE_IP="$(gcloud compute instances describe "$VM_NAME" --zone "$ZONE" --format='value(networkInterfaces[0].networkIP)')"
CONNECTION_NAME="$(gcloud sql instances describe "$SQL_INSTANCE" --format='value(connectionName)')"
SQL_PASSWORD_ENCODED="$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$SQL_PASSWORD")"

cat > "$REPO_ROOT/.gcloud/prod-runtime.env" <<EOF
PROJECT_ID=$PROJECT_ID
REGION=$REGION
ZONE=$ZONE
VM_PRIVATE_IP=$VM_PRIVATE_IP
CLOUDSQL_CONNECTION_NAME=$CONNECTION_NAME
DATABASE_URL=postgresql+asyncpg://$SQL_USER:$SQL_PASSWORD_ENCODED@/$SQL_DATABASE?host=/cloudsql/$CONNECTION_NAME
QDRANT_HOST=$VM_PRIVATE_IP
QDRANT_PORT=6333
VALKEY_URL=redis://$VM_PRIVATE_IP:6379
FRONTEND_URL=$FRONTEND_URL
MCP_BASE_URL=
EOF
chmod 600 "$REPO_ROOT/.gcloud/prod-runtime.env"

echo "Provisioned with cost guards."
echo "Runtime values saved to .gcloud/prod-runtime.env (contains secrets; do not commit)."
