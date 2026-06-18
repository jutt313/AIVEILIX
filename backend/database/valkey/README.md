# Aiveilix Valkey

Valkey stores fast temporary state for Aiveilix.

## What Valkey is used for

- refresh tokens
- JWT blacklist
- login rate limiting
- password reset tokens
- email verification tokens
- cache
- file processing queues
- embedding queues
- short-lived MCP and auth state

## Local setup

Target architecture is **Valkey**.

On this machine, `valkey-server` is not currently installed, so the local development runtime uses the available Redis-compatible server binary as a protocol-compatible stand-in.

That means:

- the key design is for `Valkey`
- backend integration should target `Valkey`
- local runtime is temporarily powered by a compatible server binary

## Local paths

- Config: `backend/database/valkey/valkey.conf`
- Data dir: `backend/database/valkey/data`
- Log file: `backend/database/valkey/logs/valkey.log`
- Socket dir: `backend/database/valkey/run`

## Local defaults

- Port: `6380`
- Bind: `127.0.0.1`

## Scripts

- `backend/database/valkey/scripts/start-local.sh`
- `backend/database/valkey/scripts/stop-local.sh`
- `backend/database/valkey/scripts/verify-local.sh`

## Local flow

```bash
./backend/database/valkey/scripts/start-local.sh
./backend/database/valkey/scripts/verify-local.sh
./backend/database/valkey/scripts/stop-local.sh
```

## Key strategy

### Refresh tokens

- `refresh_token:{token}` -> JSON payload
- TTL: `30 days`

### JWT blacklist

- `blacklist:{jti}` -> `1`
- TTL: remaining token lifetime

### Login rate limiting

- `failed_login:{email}` -> integer count
- TTL: `1 hour`

### Password reset

- `password_reset:{token}` -> `user_id`
- TTL: `1 hour`

### Email verification

- `email_verify:{token}` -> `user_id`
- TTL: `24 hours`

### Cache

- `cache:bucket:{bucket_id}` -> bucket metadata JSON
- `cache:file:{file_id}` -> file metadata JSON
- `cache:usage:{user_id}` -> usage JSON
- TTL: `5 minutes`

### Queues

- `queue:file_processing` -> list of `file_id`
- `queue:embedding` -> list of `chunk_id`
- `queue:conversation_embedding` -> list of `conversation_chunk_id`

### Optional short-lived state

- `session:{user_id}` -> current access token or session marker
- `mcp:last_used:{api_key_id}` -> last seen timestamp cache

## Notes

- Valkey data is temporary support infrastructure, not system-of-record data
- PostgreSQL remains the permanent source of truth
- Qdrant remains the vector search store
