# Aiveilix — Database Schema

> This document describes the complete database structure for Aiveilix. It covers all tables in PostgreSQL, collections in Qdrant, and keys in Redis — with column definitions, relationships, and examples for every table.

---

## Databases Overview

| Database | Purpose |
|---|---|
| **PostgreSQL** | All permanent structured data — users, buckets, files, billing, teams, auth |
| **Qdrant** | Vector embeddings for text and image semantic search |
| **Redis** | Cache, sessions, and job queues |

---

## PostgreSQL

### How Tables Relate

```
users
  |
  +——> profiles (1:1)
  |
  +——> buckets (1:many)
  |       |
  |       +——> categories (1:many)
  |       |
  |       +——> files (1:many)
  |       |       |
  |       |       +——> file_versions (1:many)
  |       |       |
  |       |       +——> chunks (1:many)
  |       |       |
  |       |       +——> summaries (1:1)
  |       |
  |       +——> conversations (1:many)
  |               |
  |               +——> messages (1:many)
  |
  +——> oauth_tokens (1:many)
  |
  +——> api_keys (1:many)
  |
  +——> subscriptions (1:1)
  |
  +——> notifications (1:many)
  |
  +——> api_usage (1:many)
  |
  +——> usage_tracking (1:many)
  |
  +——> error_logs (1:many)

team_members ——> buckets (via team_bucket_access)
team_activity_log ——> team_members
investigation_events ——> files
```

---

### Core Tables

#### `users`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `email` | VARCHAR(255) | Unique email address |
| `password_hash` | VARCHAR | Bcrypt hashed password (null for OAuth users) |
| `provider` | ENUM | `email`, `google`, `github` |
| `provider_id` | VARCHAR | External provider user ID |
| `is_verified` | BOOLEAN | Email verified status |
| `is_active` | BOOLEAN | Account active status |
| `created_at` | TIMESTAMP | Account creation time |
| `updated_at` | TIMESTAMP | Last update time |

**Example:**
```json
{
  "id": "u_abc123",
  "email": "user@example.com",
  "password_hash": "$2b$12$...",
  "provider": "email",
  "is_verified": true,
  "is_active": true,
  "created_at": "2026-03-01T10:00:00Z"
}
```

---

#### `profiles`

One profile per user. Stores display and preference information.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` |
| `full_name` | VARCHAR(255) | Display name |
| `avatar_url` | TEXT | Profile picture URL |
| `bio` | TEXT | Short user bio |
| `theme` | ENUM | `light`, `dark` |
| `language` | VARCHAR(10) | Preferred language |
| `timezone` | VARCHAR(100) | User timezone |
| `updated_at` | TIMESTAMP | Last update time |

---

#### `buckets`

Each bucket is a knowledge vault. Every bucket gets its own unique MCP URL for external AI access.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` |
| `name` | VARCHAR(255) | Bucket display name |
| `description` | TEXT | Optional description |
| `mcp_url` | TEXT | Unique bucket MCP URL |
| `mcp_token` | VARCHAR | Auth token baked into bucket MCP URL |
| `account_mcp_url` | TEXT | Account-level MCP URL for managing all buckets |
| `account_mcp_token` | VARCHAR | Auth token for account MCP URL |
| `color` | VARCHAR(7) | Hex color for UI display |
| `icon` | VARCHAR(50) | Icon identifier |
| `is_public` | BOOLEAN | Public or private bucket |
| `storage_used` | BIGINT | Storage used in bytes |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Last update time |

**Example:**
```json
{
  "id": "b_xyz789",
  "user_id": "u_abc123",
  "name": "Company Research",
  "mcp_url": "https://mcp.aiveilix.com/bucket/tok_abc123xyz",
  "mcp_token": "tok_abc123xyz",
  "account_mcp_url": "https://mcp.aiveilix.com/account/acc_tok_789",
  "account_mcp_token": "acc_tok_789",
  "is_public": false,
  "storage_used": 52428800,
  "created_at": "2026-03-10T09:00:00Z"
}
```

---

#### `categories`

Organizes files inside a bucket into groups.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `bucket_id` | UUID | Foreign key — `buckets.id` |
| `name` | VARCHAR(255) | Category name |
| `color` | VARCHAR(7) | Hex color |
| `created_at` | TIMESTAMP | Creation time |

---

#### `files`

Stores metadata for every uploaded file.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `bucket_id` | UUID | Foreign key — `buckets.id` |
| `user_id` | UUID | Foreign key — `users.id` |
| `category_id` | UUID | Foreign key — `categories.id` (optional) |
| `name` | VARCHAR(255) | Original file name |
| `type` | VARCHAR(50) | File type: `pdf`, `docx`, `image`, etc. |
| `size` | BIGINT | File size in bytes |
| `r2_path` | TEXT | Raw file path in Cloudflare R2 |
| `layout_json_path` | TEXT | Layout JSON Map path in Cloudflare R2 |
| `status` | ENUM | `uploading`, `processing`, `ready`, `failed` |
| `page_count` | INTEGER | Total pages in document |
| `version` | INTEGER | Current version number |
| `created_at` | TIMESTAMP | Upload time |
| `updated_at` | TIMESTAMP | Last update time |

**Example:**
```json
{
  "id": "f_abc123",
  "bucket_id": "b_xyz789",
  "user_id": "u_abc123",
  "name": "company-report.pdf",
  "type": "pdf",
  "size": 2048000,
  "r2_path": "raw/f_abc123/company-report.pdf",
  "layout_json_path": "layouts/f_abc123/layout.json",
  "status": "ready",
  "page_count": 10,
  "version": 1,
  "created_at": "2026-03-15T08:00:00Z"
}
```

---

#### `file_versions`

Tracks every version of a file when it is re-uploaded or updated.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `file_id` | UUID | Foreign key — `files.id` |
| `version_number` | INTEGER | Version number |
| `r2_path` | TEXT | Path to this version in Cloudflare R2 |
| `size` | BIGINT | File size in bytes |
| `created_at` | TIMESTAMP | Version creation time |

---

#### `chunks`

Stores metadata for every text chunk. The actual vector is stored in Qdrant, referenced by the same `id`.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key — same ID used in Qdrant |
| `file_id` | UUID | Foreign key — `files.id` |
| `bucket_id` | UUID | Foreign key — `buckets.id` |
| `page` | INTEGER | Page number this chunk came from |
| `content` | TEXT | The actual chunk text |
| `block_id` | VARCHAR | Block ID from Layout JSON Map |
| `nearby_image_id` | VARCHAR | Nearby image ID from Layout JSON Map |
| `token_count` | INTEGER | Number of tokens in this chunk |
| `status` | ENUM | `pending`, `embedded`, `failed` |
| `retry_count` | INTEGER | Number of embedding retry attempts |
| `created_at` | TIMESTAMP | Creation time |

---

#### `summaries`

Stores AI-generated summaries for files and buckets.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `file_id` | UUID | Foreign key — `files.id` (optional) |
| `bucket_id` | UUID | Foreign key — `buckets.id` (optional) |
| `content` | TEXT | Summary text |
| `created_at` | TIMESTAMP | Creation time |

---

#### `conversations`

Stores chat sessions between a user and their bucket.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` |
| `bucket_id` | UUID | Foreign key — `buckets.id` |
| `title` | VARCHAR(255) | Auto-generated conversation title |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Last message time |

---

#### `messages`

Stores every message in a conversation.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `conversation_id` | UUID | Foreign key — `conversations.id` |
| `role` | ENUM | `user`, `assistant` |
| `content` | TEXT | Message content |
| `chunks_used` | JSONB | Array of chunk IDs used to generate answer |
| `created_at` | TIMESTAMP | Message time |

---

### OAuth and MCP Tables

#### `oauth_authorization_codes`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` |
| `code` | VARCHAR | The authorization code |
| `code_challenge` | VARCHAR | PKCE code challenge |
| `redirect_uri` | TEXT | Redirect URI |
| `expires_at` | TIMESTAMP | Expiry time |
| `used` | BOOLEAN | Whether code has been used |
| `created_at` | TIMESTAMP | Creation time |

---

#### `oauth_tokens`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` |
| `access_token` | VARCHAR | JWT access token |
| `refresh_token` | VARCHAR | Refresh token |
| `provider` | ENUM | `email`, `google`, `github` |
| `expires_at` | TIMESTAMP | Access token expiry |
| `created_at` | TIMESTAMP | Creation time |

---

#### `api_keys`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` |
| `bucket_id` | UUID | Foreign key — `buckets.id` (null for account-level keys) |
| `token` | VARCHAR | The MCP token |
| `type` | ENUM | `bucket`, `account` |
| `name` | VARCHAR(255) | Friendly name |
| `last_used_at` | TIMESTAMP | Last time this key was used |
| `is_active` | BOOLEAN | Active status |
| `created_at` | TIMESTAMP | Creation time |

---

### Team Management Tables

#### `team_members`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `owner_user_id` | UUID | Foreign key — `users.id` (bucket owner) |
| `member_user_id` | UUID | Foreign key — `users.id` (team member) |
| `role` | ENUM | `viewer`, `editor`, `admin` |
| `status` | ENUM | `pending`, `accepted`, `rejected` |
| `created_at` | TIMESTAMP | Invite time |

---

#### `team_bucket_access`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `team_member_id` | UUID | Foreign key — `team_members.id` |
| `bucket_id` | UUID | Foreign key — `buckets.id` |
| `permission` | ENUM | `read`, `write`, `admin` |
| `created_at` | TIMESTAMP | Access grant time |

---

#### `team_activity_log`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `team_member_id` | UUID | Foreign key — `team_members.id` |
| `bucket_id` | UUID | Foreign key — `buckets.id` |
| `action` | VARCHAR(255) | Action performed |
| `metadata` | JSONB | Additional action details |
| `created_at` | TIMESTAMP | Action time |

---

### Billing and Usage Tables

#### `subscriptions`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` |
| `plan` | ENUM | `free`, `individual`, `team`, `business` |
| `stripe_customer_id` | VARCHAR | Stripe customer ID |
| `stripe_subscription_id` | VARCHAR | Stripe subscription ID |
| `status` | ENUM | `active`, `cancelled`, `past_due` |
| `current_period_end` | TIMESTAMP | Current billing period end |
| `created_at` | TIMESTAMP | Subscription start time |

---

#### `api_usage`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` |
| `bucket_id` | UUID | Foreign key — `buckets.id` (optional) |
| `api_key_id` | UUID | Foreign key — `api_keys.id` |
| `endpoint` | VARCHAR(255) | API endpoint called |
| `tokens_used` | INTEGER | Tokens consumed in this call |
| `created_at` | TIMESTAMP | Call time |

---

#### `usage_tracking`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` |
| `month` | DATE | Month being tracked |
| `storage_used` | BIGINT | Total storage used in bytes |
| `chat_messages_count` | INTEGER | Total chat messages sent |
| `mcp_calls_count` | INTEGER | Total MCP calls made |
| `buckets_count` | INTEGER | Total buckets created |
| `files_count` | INTEGER | Total files uploaded |
| `updated_at` | TIMESTAMP | Last update time |

---

### System Tables

#### `notifications`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` |
| `type` | ENUM | `info`, `success`, `warning`, `error` |
| `title` | VARCHAR(255) | Notification title |
| `message` | TEXT | Notification message |
| `is_read` | BOOLEAN | Read status |
| `created_at` | TIMESTAMP | Creation time |

---

#### `investigation_events`

Tracks the full processing timeline for every file.

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `file_id` | UUID | Foreign key — `files.id` |
| `event` | VARCHAR(255) | Event name |
| `status` | ENUM | `started`, `completed`, `failed` |
| `metadata` | JSONB | Additional event details |
| `created_at` | TIMESTAMP | Event time |

**Example events in order:**
```
docling_started
docling_completed
gemini_started
gemini_completed
layout_json_created
chunking_started
chunking_completed
embedding_started
embedding_completed
file_ready
```

---

#### `error_logs`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key — `users.id` (optional) |
| `file_id` | UUID | Foreign key — `files.id` (optional) |
| `service` | VARCHAR(100) | Service that threw the error |
| `error_message` | TEXT | Error message |
| `stack_trace` | TEXT | Full stack trace |
| `resolved` | BOOLEAN | Whether error has been resolved |
| `created_at` | TIMESTAMP | Error time |

---

## Qdrant

### `text_chunks` Collection

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Same as `chunks.id` in PostgreSQL |
| `vector` | float[] | BGE-M3 dense vector (1024 dimensions) |
| `sparse_vector` | sparse | BGE-M3 sparse vector for BM25 keyword search |
| `payload.file_id` | UUID | Reference to `files.id` |
| `payload.bucket_id` | UUID | Reference to `buckets.id` |
| `payload.page` | INTEGER | Page number |
| `payload.content` | TEXT | Chunk text content |
| `payload.nearby_image_id` | VARCHAR | Nearby image ID from Layout JSON |
| `payload.image_description` | TEXT | Description of nearby image |
| `payload.image_text_inside` | TEXT | Text extracted from nearby image |
| `payload.status` | ENUM | `active`, `deprecated` |

**Example:**
```json
{
  "id": "chunk_001",
  "vector": [0.012, 0.843, 0.231, "..."],
  "payload": {
    "file_id": "f_abc123",
    "bucket_id": "b_xyz789",
    "page": 1,
    "content": "Total revenue increased by 23% this quarter.",
    "nearby_image_id": "img_1",
    "image_description": "A blue bar chart showing monthly revenue growth.",
    "image_text_inside": "July: $200k, August: $230k, September: $260k",
    "status": "active"
  }
}
```

---

### `image_chunks` Collection

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique image chunk ID |
| `vector` | float[] | CLIP image vector (512 dimensions) |
| `payload.file_id` | UUID | Reference to `files.id` |
| `payload.bucket_id` | UUID | Reference to `buckets.id` |
| `payload.page` | INTEGER | Page number |
| `payload.image_id` | VARCHAR | Image ID from Layout JSON |
| `payload.description` | TEXT | Gemini Flash image description |
| `payload.text_inside` | TEXT | Text extracted from image |
| `payload.nearby_text_id` | VARCHAR | Nearby text block ID |
| `payload.status` | ENUM | `active`, `deprecated` |

---

## Redis

### Session Tokens
```
session:{user_id} → JWT token
TTL: 24 hours
```

### Job Queues
```
queue:file_processing → list of file_ids waiting to be processed
queue:embedding → list of chunk_ids waiting to be embedded
```

### Cache
```
cache:bucket:{bucket_id} → bucket metadata JSON — TTL: 5 minutes
cache:file:{file_id} → file metadata JSON — TTL: 5 minutes
cache:usage:{user_id} → current usage stats JSON — TTL: 5 minutes
```

---

## How All Three Databases Work Together

```
User sends query to bucket
        |
        v
Redis checks session token (auth)
        |
        v
Qdrant hybrid search on text_chunks
(dense BGE-M3 + sparse BM25)
        |
        v
BGE Reranker selects top 5 chunks
        |
        v
PostgreSQL fetches full metadata
for each chunk (file name, page, bucket)
        |
        v
Layout JSON from Cloudflare R2
adds positional context
        |
        v
Claude API generates answer
        |
        v
Message saved to PostgreSQL (messages table)
Usage updated in Redis cache + PostgreSQL (usage_tracking)
        |
        v
Answer returned to user
```

---

*Document version: 1.0 — March 2026*
