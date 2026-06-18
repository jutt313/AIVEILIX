# AIveilix Google Cloud Deploy

This deploy setup is for a production-grade performance test, not an unlimited launch.
Defaults are intentionally capped to avoid surprise spend.

## Current Blocker

The active `gcloud` account must have access to project `aiveilix-499209`.
Right now, `botuvic@gmail.com` does not have permission.

Grant that account Owner/Editor temporarily, or run:

```bash
gcloud auth login
gcloud config set project aiveilix-499209
firebase login
```

## Cost Guards

Default caps in `config.env.example`:

- Cloud Run max instances: `3`
- Cloud Run min instances: `0`
- Cloud SQL: zonal, fixed 20GB SSD, no storage auto-increase
- Qdrant + Valkey: one `e2-medium` VM
- Qdrant/Valkey ports: no public firewall rule is created
- Resource labels: `app=aiveilix,env=prod-test,owner=codex`

Optional budget alert:

```bash
cp deploy/gcp/config.env.example deploy/gcp/config.env
BILLING_ACCOUNT_ID=000000-000000-000000 MONTHLY_BUDGET_USD=100 deploy/gcp/create-budget-alert.sh
```

## Run Order

```bash
cp deploy/gcp/config.env.example deploy/gcp/config.env

# 1. Create capped infrastructure.
deploy/gcp/provision.sh

# 2. Build image, sync Secret Manager, run Alembic, deploy Cloud Run.
deploy/gcp/deploy-backend.sh

# 3. Build Vite with the Cloud Run URL and deploy Firebase Hosting.
deploy/gcp/deploy-frontend.sh
```

## What Gets Created

- Artifact Registry repo
- Serverless VPC Access connector
- Compute Engine VM for Qdrant + Valkey
- Persistent disk for Qdrant + Valkey data
- Cloud SQL PostgreSQL
- Secret Manager secrets from root `.env`
- Cloud Run migration job
- Cloud Run backend service
- Firebase Hosting frontend

## Notes

- R2 remains external and is read from root `.env`.
- Custom app/API/MCP domains can be added after the default URLs work.
- If performance is slow, scale in this order: Cloud Run min instances, Cloud SQL tier/indexes, Qdrant VM size/disk, then caching.
