#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/config.env}"
ROOT_ENV="$REPO_ROOT/.env"
RUNTIME_ENV="$REPO_ROOT/.gcloud/prod-runtime.env"
TMP_ROOT="${TMPDIR:-$REPO_ROOT/.tmp}"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Missing $CONFIG_FILE. Copy deploy/gcp/config.env.example to deploy/gcp/config.env first." >&2
  exit 1
fi
if [ ! -f "$ROOT_ENV" ]; then
  echo "Missing root .env at $ROOT_ENV." >&2
  exit 1
fi

set -a
source "$CONFIG_FILE"
source "$ROOT_ENV"
if [ -f "$RUNTIME_ENV" ]; then
  source "$RUNTIME_ENV"
fi
set +a

gcloud config set project "$PROJECT_ID" >/dev/null

SECRET_KEYS=(
  SECRET_KEY ADMIN_API_KEY ADMIN_EMAILS ADMIN_PHONE
  DATABASE_URL
  QDRANT_URL QDRANT_API_KEY QDRANT_HOST QDRANT_PORT VALKEY_URL
  R2_ACCOUNT_ID R2_ACCESS_KEY_ID R2_SECRET_ACCESS_KEY R2_BUCKET_NAME R2_PUBLIC_URL
  GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET GITHUB_CLIENT_ID GITHUB_CLIENT_SECRET
  GEMINI_API_KEY GEMINI_VISUAL_MODEL
  LLM_PROVIDER ANTHROPIC_API_KEY OPENAI_API_KEY
  DEEPSEEK_API_KEY DEEPSEEK_BASE_URL
  MOONSHOT_API_KEY MOONSHOT_BASE_URL MOONSHOT_VISUAL_MODEL
  MINIMAX_API_KEY MINIMAX_BASE_URL MINIMAX_MODEL
  PROCESSING_V3_AI_SUMMARY
  MISTRAL_API_KEY VOYAGE_API_KEY
  STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET STRIPE_PRICE_INDIVIDUAL STRIPE_PRICE_TEAM
  FRONTEND_URL FRONTEND_ALLOWED_ORIGINS MCP_BASE_URL
  SMTP_HOST SMTP_PORT SMTP_USER SMTP_PASSWORD SMTP_FROM_EMAIL SMTP_FROM_NAME
  AGENTIC_RAG_LOOP_ENABLED AGENTIC_RAG_LOOP_MAX_SUBQUESTIONS
  AGENTIC_RAG_LOOP_MAX_RETRIES_PER_SUBQUESTION
  AGENTIC_RAG_LOOP_DOC_LIMIT_PER_SUBQUESTION
  AGENTIC_RAG_LOOP_WEB_LIMIT_PER_SUBQUESTION
  AGENTIC_RAG_LOOP_MAX_TOTAL_SEARCHES
)

mkdir -p "$REPO_ROOT/.gcloud"
mkdir -p "$TMP_ROOT"
SECRETS_ARG_FILE="$REPO_ROOT/.gcloud/cloudrun-set-secrets.txt"
: > "$SECRETS_ARG_FILE"

for key in "${SECRET_KEYS[@]}"; do
  value="${!key-}"
  if [ -z "${value}" ]; then
    continue
  fi

  if ! gcloud secrets describe "$key" >/dev/null 2>&1; then
    gcloud secrets create "$key" \
      --replication-policy=automatic \
      --labels="$LABELS" >/dev/null
  fi
  tmp_secret_file="$(mktemp "$TMP_ROOT/aiveilix-secret.XXXXXX")"
  chmod 600 "$tmp_secret_file"
  printf '%s' "$value" > "$tmp_secret_file"
  if ! gcloud secrets versions add "$key" --data-file="$tmp_secret_file" >/dev/null; then
    rm -f "$tmp_secret_file"
    exit 1
  fi
  rm -f "$tmp_secret_file"

  if [ -s "$SECRETS_ARG_FILE" ]; then
    printf ',' >> "$SECRETS_ARG_FILE"
  fi
  printf '%s=%s:latest' "$key" "$key" >> "$SECRETS_ARG_FILE"
done

echo "Secrets synced. Names only written to .gcloud/cloudrun-set-secrets.txt."
