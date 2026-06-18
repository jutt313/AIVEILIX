# Aiveilix Database

PostgreSQL is the source of truth for the Aiveilix relational data model.

Supporting stores:

- `Qdrant` for vector search
- `Valkey` for temporary fast state

This workspace includes:

- `postgres/migrations/2026-04-01_initial_schema.sql`
- `postgres/scripts/start-local.sh`
- `postgres/scripts/stop-local.sh`
- `postgres/scripts/apply-schema.sh`

Local defaults:

- Database name: `aiveilix`
- Port: `5433`
- Socket dir: `backend/database/postgres/run`
- Data dir: `backend/database/postgres/data`

Typical local flow (from repo root):

```bash
./backend/database/postgres/scripts/start-local.sh
./backend/database/postgres/scripts/apply-schema.sh
./backend/database/qdrant/scripts/setup-env.sh
./backend/database/qdrant/scripts/bootstrap-local.sh
./backend/database/valkey/scripts/start-local.sh
./backend/database/postgres/scripts/stop-local.sh
./backend/database/valkey/scripts/stop-local.sh
```

### “relation users does not exist” (empty database)

The API expects tables from `postgres/migrations/`. If `DATABASE_URL` points at a fresh or non-bootstrapped database, apply the schema using the same URL as the backend:

```bash
set -a && source .env && set +a
./backend/database/postgres/scripts/apply-schema-env.sh
```

That runs the initial SQL migrations and then `alembic upgrade head`. Safe to run again: if `public.users` already exists, the initial SQL file is skipped so you do not get duplicate `CREATE TYPE` errors.
