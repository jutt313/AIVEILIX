#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/config.env}"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Missing $CONFIG_FILE. Copy deploy/gcp/config.env.example to deploy/gcp/config.env first." >&2
  exit 1
fi

set -a
source "$CONFIG_FILE"
set +a

: "${BILLING_ACCOUNT_ID:?Set BILLING_ACCOUNT_ID, for example 000000-000000-000000}"
MONTHLY_BUDGET_USD="${MONTHLY_BUDGET_USD:-100}"
MONTHLY_BUDGET_CURRENCY="${MONTHLY_BUDGET_CURRENCY:-USD}"

gcloud config set project "$PROJECT_ID" >/dev/null
gcloud billing budgets create \
  --billing-account="$BILLING_ACCOUNT_ID" \
  --display-name="AIveilix guarded prod-test budget" \
  --budget-amount="${MONTHLY_BUDGET_USD}${MONTHLY_BUDGET_CURRENCY}" \
  --filter-projects="projects/$PROJECT_ID" \
  --threshold-rule=percent=0.5 \
  --threshold-rule=percent=0.9 \
  --threshold-rule=percent=1.0

echo "Budget alert created for $PROJECT_ID at ${MONTHLY_BUDGET_USD}${MONTHLY_BUDGET_CURRENCY}/month."
