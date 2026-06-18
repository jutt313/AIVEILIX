# Aiveilix — DB Progress

> Running progress log for the database build. This file tracks what has already been completed, the current local setup, and what comes next.

---

## Status

**Current phase:** PostgreSQL foundation completed + Qdrant local collections completed + Valkey local layer verified

**Date:** 2026-04-01

**Current database name:** `aiveilix`

> Note: PostgreSQL database names are typically created in lowercase for simplicity. This is the working local database for Aiveilix.

---

## What Has Been Done

### 1. Local database workspace created

Created database workspace structure under:

- `database/`
- `database/postgres/`
- `database/postgres/migrations/`
- `database/postgres/scripts/`
- `database/postgres/data/`
- `database/postgres/logs/`
- `database/postgres/run/`

---

### 2. Initial PostgreSQL schema created

Created the full bootstrap migration:

- `database/postgres/migrations/2026-04-01_initial_schema.sql`

This migration includes:

- PostgreSQL extensions
- all enums
- all tables
- foreign keys
- constraints
- indexes
- update triggers
- conversation thread limit trigger
- schema migration tracking

---

### 3. Local PostgreSQL helper scripts created

Created:

- `database/postgres/scripts/start-local.sh`
- `database/postgres/scripts/apply-schema.sh`
- `database/postgres/scripts/stop-local.sh`

These scripts handle:

- local PostgreSQL startup
- creating the `aiveilix` database
- applying the schema
- stopping the local database

---

### 4. Local PostgreSQL instance started

Local PostgreSQL is running with:

- **Port:** `5433`
- **Socket dir:** `database/postgres/run`
- **Data dir:** `database/postgres/data`

Reason for custom local setup:

- avoids conflict with any system PostgreSQL on default port `5432`
- keeps the full local DB inside the project workspace

---

### 5. Schema applied successfully

The migration was applied successfully into the local `aiveilix` database.

Verified directly from PostgreSQL:

- all intended public tables exist
- all enum types exist
- schema migration record inserted

---

### 6. Qdrant local setup created

Created Qdrant workspace structure under:

- `database/qdrant/`
- `database/qdrant/data/local/`
- `database/qdrant/scripts/`

Created files:

- `database/qdrant/README.md`
- `database/qdrant/requirements.txt`
- `database/qdrant/bootstrap_collections.py`
- `database/qdrant/scripts/setup-env.sh`
- `database/qdrant/scripts/bootstrap-local.sh`
- `database/qdrant/scripts/verify-local.sh`

---

### 7. Qdrant dependency installed

Installed local Python dependency into:

- `database/.venv`

Installed package:

- `qdrant-client`

---

### 8. Qdrant collections created successfully

Created and verified these local collections:

- `text_chunks`
- `image_chunks`
- `conversation_chunks`

Current status:

- collections exist
- point counts are `0`
- ready for document and conversation embeddings

---

### 8.1 Qdrant compatibility issue resolved

Problem found:

- backend runtime had `qdrant-client 1.12.1`
- database bootstrap tools had `qdrant-client 1.17.1`
- local embedded Qdrant store had been created with the newer client format

Fix applied:

- aligned backend and database-tooling to `qdrant-client 1.17.1`
- verified backend runtime can now open the local embedded store successfully

Result:

- no local Qdrant data reset was needed
- backend can read:
  - `text_chunks`
  - `image_chunks`
  - `conversation_chunks`

---

### 9. Valkey local layer created

Created Valkey workspace structure under:

- `database/valkey/`
- `database/valkey/scripts/`
- `database/valkey/data/`
- `database/valkey/logs/`
- `database/valkey/run/`

Created files:

- `database/valkey/README.md`
- `database/valkey/valkey.conf`
- `database/valkey/scripts/start-local.sh`
- `database/valkey/scripts/stop-local.sh`
- `database/valkey/scripts/verify-local.sh`

---

### 10. Valkey key strategy defined

Defined key structure for:

- refresh tokens
- JWT blacklist
- failed login rate limiting
- password reset tokens
- email verification tokens
- cache
- file processing queues
- embedding queues
- conversation embedding queue

---

### 11. Valkey local runtime verified

Verified local cache layer with:

- `PING` -> `PONG`
- key write
- key read
- key delete

Current local runtime:

- target architecture: `Valkey`
- local binary in use on this machine: Redis-compatible server
- verified port: `6380`

---

## Tables Created

### Core user and bucket tables

- `users`
- `profiles`
- `buckets`
- `categories`
- `files`
- `file_versions`
- `chunks`
- `summaries`

### Conversation and memory tables

- `conversations`
- `messages`
- `conversation_chunks`

### Auth and MCP tables

- `oauth_authorization_codes`
- `oauth_tokens`
- `api_keys`

### Team tables

- `team_members`
- `team_bucket_access`
- `team_activity_log`

### Billing and usage tables

- `subscriptions`
- `api_usage`
- `usage_tracking`

### System tables

- `notifications`
- `investigation_events`
- `error_logs`

### Helper table

- `schema_migrations`

---

## Important DB Decisions Already Included

### Conversation RAG memory support

Added:

- `conversation_chunks` table for thread-level conversation memory
- `messages.token_count`
- `messages.embedding_status`
- `messages.parent_message_id`

This supports:

- long conversation memory
- future Qdrant embeddings for chat history
- thread-level RAG retrieval

---

### Qdrant vector layout support

Defined local Qdrant collections for:

- document text vectors
- image vectors
- conversation memory vectors

Collection plan:

- `text_chunks` → dense `1024` + sparse support
- `image_chunks` → dense `512`
- `conversation_chunks` → dense `1024` + sparse support

---

### Valkey temporary-state layout support

Defined Valkey usage for:

- auth temporary state
- rate limiting
- short-lived tokens
- cache
- background queues

Key examples:

- `refresh_token:{token}`
- `blacklist:{jti}`
- `failed_login:{email}`
- `password_reset:{token}`
- `email_verify:{token}`
- `cache:bucket:{bucket_id}`
- `queue:file_processing`
- `queue:embedding`
- `queue:conversation_embedding`

---

### Agent thread controls

Added to `conversations`:

- `web_search_mode`
- `follow_up_mode`

This supports the agent behavior defined in `agent.md`.

---

### User profile AI settings

Added to `profiles`:

- `preferred_llm`
- `follow_up_mode`

This supports:

- user LLM selection
- user clarification preference

---

### Security support

Added to `users`:

- `two_factor_enabled`
- `two_factor_secret`
- `two_factor_backup_codes`

This supports the 2FA system described in the auth docs.

---

## Enums Created

- `auth_provider`
- `theme_mode`
- `llm_provider`
- `subscription_plan`
- `subscription_status`
- `file_status`
- `embedding_status`
- `message_role`
- `api_key_type`
- `team_role`
- `team_member_status`
- `team_bucket_permission`
- `notification_type`
- `event_status`
- `web_search_mode`
- `follow_up_mode`

---

## Notes From Setup

- `psql` was available locally
- no PostgreSQL server was running initially
- a local project-level PostgreSQL cluster was initialized
- local startup required running outside the sandbox because PostgreSQL needed shared memory access
- after startup, the schema was applied successfully

---

## Files Created So Far

- `database/README.md`
- `database/postgres/migrations/2026-04-01_initial_schema.sql`
- `database/postgres/scripts/start-local.sh`
- `database/postgres/scripts/apply-schema.sh`
- `database/postgres/scripts/stop-local.sh`
- `database/qdrant/README.md`
- `database/qdrant/requirements.txt`
- `database/qdrant/bootstrap_collections.py`
- `database/qdrant/scripts/setup-env.sh`
- `database/qdrant/scripts/bootstrap-local.sh`
- `database/qdrant/scripts/verify-local.sh`
- `database/valkey/README.md`
- `database/valkey/valkey.conf`
- `database/valkey/scripts/start-local.sh`
- `database/valkey/scripts/stop-local.sh`
- `database/valkey/scripts/verify-local.sh`

---

## What Comes Next

### Next database components

1. **Seed data**
   - add sample user
   - add sample bucket
   - add sample file and conversation data for testing

2. **Backend DB integration**
   - connect backend config to PostgreSQL
   - connect backend config to Qdrant
   - connect backend config to Valkey

---

## Qdrant Notes

- local development uses Qdrant embedded mode through `qdrant-client`
- this works well for local setup and schema bootstrapping
- embedded local mode does not give full server behavior for payload indexes
- for production or full concurrent access, use a real Qdrant server or Qdrant Cloud

---

## Current Summary

PostgreSQL foundation is now in place.

The relational schema is ready for:

- auth
- users and profiles
- buckets and files
- document chunk metadata
- conversation threads
- conversation RAG memory
- billing and usage tracking
- team access
- MCP keys
- notifications and processing events

Next step is to add seed/test data and then wire the backend to PostgreSQL, Qdrant, and Valkey.

---

*Progress log started: 2026-04-01*
