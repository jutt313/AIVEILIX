# API Reference

Complete API documentation for AIveilix - AI-Powered Knowledge Management Platform

---

## Table of Contents

1. [Introduction](#introduction)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
   - [JWT Authentication](#jwt-authentication)
   - [API Key Authentication](#api-key-authentication)
   - [OAuth2 Authentication](#oauth2-authentication)
4. [Endpoints](#endpoints)
   - [Auth Endpoints](#auth-endpoints)
   - [Buckets Endpoints](#buckets-endpoints)
   - [Files Endpoints](#files-endpoints)
   - [Chat Endpoints](#chat-endpoints)
   - [API Keys Endpoints](#api-keys-endpoints)
   - [MCP Endpoints](#mcp-endpoints)
   - [OAuth Endpoints](#oauth-endpoints)
   - [Notifications Endpoints](#notifications-endpoints)
5. [Rate Limits](#rate-limits)
6. [Pricing Plans](#pricing-plans)
7. [Error Handling](#error-handling)
8. [Code Examples](#code-examples)

---

## Introduction

The AIveilix API is a RESTful API that allows you to manage your knowledge buckets, upload documents, perform semantic searches, and interact with AI to analyze your data.

**Key Features:**
- **Comprehensive Document Processing**: Upload 50+ file types
- **AI-Powered Chat**: DeepSeek Reasoner with extended thinking
- **Vector Search**: 3072-dimension embeddings (OpenAI text-embedding-3-large)
- **MCP Protocol**: Integrate with Cursor, ChatGPT, Claude Desktop
- **OAuth2 Support**: Secure third-party access

**API Version:** v1
**Current Year:** 2026
**Protocol:** HTTPS only
**Data Format:** JSON

---

## Base URL

```
Production: https://api.aiveilix.com
Development: http://localhost:7223
```

All endpoints are prefixed with `/api` unless specified otherwise (MCP endpoints use `/mcp`).

---

## Authentication

AIveilix supports three authentication methods:

### JWT Authentication

**Used for:** Web application, mobile apps

**How it works:**
1. User signs up or logs in
2. Server returns `access_token` and `refresh_token`
3. Client stores tokens (localStorage recommended)
4. Include token in all requests

**Header Format:**
```
Authorization: Bearer <access_token>
```

**Token Expiration:**
- Access Token: 60 minutes
- Refresh Token: 30 days

**Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/buckets" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### API Key Authentication

**Used for:** MCP integration, CLI tools, external services

**How it works:**
1. Create API key via dashboard or `/api/api-keys` endpoint
2. Key is returned ONCE (format: `aiveilix_sk_live_<random>`)
3. Store key securely
4. Include key in Authorization header

**Header Format:**
```
Authorization: Bearer aiveilix_sk_live_<your_key>
```

**Key Features:**
- **SHA-256 hashing** for security
- **Scoped permissions** (read, write, delete)
- **Bucket restrictions** (optional)
- **Usage tracking** (last_used_at, request_count)
- **Expiration support** (optional)

**Security Notes:**
- Keys are hashed before storage (irreversible)
- Only prefix is stored in plaintext (first 12 chars)
- Full key never retrievable after creation
- Revoke compromised keys immediately

**Example:**
```bash
curl -X GET "https://api.aiveilix.com/mcp/buckets" \
  -H "Authorization: Bearer aiveilix_sk_live_abc123def456..."
```

---

### OAuth2 Authentication

**Used for:** ChatGPT integration, third-party apps

**Grant Types:**
- **Authorization Code** with PKCE support
- **Refresh Token**

**Flow:**
1. Register OAuth client (`POST /api/oauth/clients`)
2. Redirect user to authorization URL
3. User approves access
4. Exchange code for access token
5. Use token to access API

**Token Expiration:**
- Access Token: 60 minutes
- Refresh Token: 30 days
- Auth Code: 10 minutes (one-time use)

**Scopes:**
- `read`: View buckets, files, search
- `write`: Upload files, create buckets
- `query`: Semantic search
- `chat`: AI chat capabilities
- `full`: All permissions

**Example Authorization URL:**
```
https://api.aiveilix.com/oauth/authorize?
  client_id=<client_id>&
  redirect_uri=https://yourapp.com/callback&
  response_type=code&
  scope=read+write+query+chat&
  state=<random_state>&
  code_challenge=<pkce_challenge>&
  code_challenge_method=S256
```

---

## Endpoints

### Auth Endpoints

Base path: `/api/auth`

---

#### 1. Sign Up

Create a new user account.

**Endpoint:** `POST /api/auth/signup`

**Authentication:** None (public)

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Account created. Please check your email to verify.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

**Validation Rules:**
- Email: Valid email format, unique
- Password: Minimum 6 characters
- Full Name: Optional

**Email Verification:**
- Verification email sent automatically via Supabase Auth
- User must verify email before login (optional enforcement)

**Error Responses:**
```json
{
  "success": false,
  "message": "Email already registered"
}
```

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe"
  }'
```

---

#### 2. Login

Authenticate user and receive tokens.

**Endpoint:** `POST /api/auth/login`

**Authentication:** None (public)

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe"
  },
  "session": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": 1704067200
  }
}
```

**On Successful Login:**
- Login notification created automatically
- Access token valid for 60 minutes
- Refresh token valid for 30 days

**Error Responses:**
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

---

#### 3. Logout

Sign out the current user.

**Endpoint:** `POST /api/auth/logout`

**Authentication:** JWT (optional)

**Request Body:** None

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/auth/logout" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 4. Get Current User

Retrieve current user information from token.

**Endpoint:** `GET /api/auth/me`

**Authentication:** JWT required

**Response:** 200 OK
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `401 Unauthorized`: Token expired

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 5. Forgot Password

Request password reset email.

**Endpoint:** `POST /api/auth/forgot-password`

**Authentication:** None (public)

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** 200 OK
```json
{
  "success": true,
  "message": "If an account exists, a password reset link has been sent."
}
```

**Security Note:**
- Response doesn't reveal if email exists (prevents enumeration)
- Custom email sent via email_service
- Reset link redirects to frontend: `{frontend_url}/reset-password`

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

---

#### 6. Reset Password

Reset password using token from email.

**Endpoint:** `POST /api/auth/reset-password`

**Authentication:** None (uses token from email)

**Request Body:**
```json
{
  "new_password": "NewSecurePassword123!"
}
```

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

**Error Responses:**
```json
{
  "success": false,
  "message": "Failed to reset password"
}
```

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "NewSecurePassword123!"
  }'
```

---

#### 7. Change Password

Change password for logged-in user (requires current password).

**Endpoint:** `POST /api/auth/change-password`

**Authentication:** JWT required

**Request Body:**
```json
{
  "current_password": "CurrentPassword123!",
  "new_password": "NewSecurePassword456!"
}
```

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Validation:**
1. Verify current password (attempts login)
2. If current password correct, update to new password
3. New session created automatically

**Error Responses:**
```json
{
  "success": false,
  "message": "Current password is incorrect"
}
```

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/auth/change-password" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "CurrentPassword123!",
    "new_password": "NewSecurePassword456!"
  }'
```

---

#### 8. Delete Account

Permanently delete user account (requires password verification).

**Endpoint:** `POST /api/auth/delete-account`

**Authentication:** JWT required

**Request Body:**
```json
{
  "password": "CurrentPassword123!"
}
```

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Account deleted successfully"
}
```

**Cascade Deletions:**
- All buckets deleted
- All files deleted from storage
- All chunks and embeddings deleted
- All conversations and messages deleted
- All API keys revoked
- All OAuth clients revoked

**Security:**
- Password verification required
- Uses admin API for deletion
- Irreversible action

**Error Responses:**
```json
{
  "success": false,
  "message": "Password is incorrect"
}
```

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/auth/delete-account" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "CurrentPassword123!"
  }'
```

---

### Buckets Endpoints

Base path: `/api/buckets`

---

#### 1. List Buckets

Get all buckets for the current user.

**Endpoint:** `GET /api/buckets`

**Authentication:** JWT required

**Response:** 200 OK
```json
{
  "buckets": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "440e8400-e29b-41d4-a716-446655440000",
      "name": "Research Papers",
      "description": "Academic papers collection",
      "is_private": true,
      "file_count": 15,
      "total_size_bytes": 52428800,
      "created_at": "2026-01-15T10:30:00Z",
      "updated_at": "2026-02-01T14:20:00Z"
    }
  ],
  "total": 1
}
```

**Sorting:**
- Ordered by `created_at` descending (newest first)

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/buckets" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 2. Create Bucket

Create a new knowledge bucket.

**Endpoint:** `POST /api/buckets`

**Authentication:** JWT required

**Request Body:**
```json
{
  "name": "Research Papers",
  "description": "Academic papers collection"
}
```

**Response:** 200 OK
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "440e8400-e29b-41d4-a716-446655440000",
  "name": "Research Papers",
  "description": "Academic papers collection",
  "is_private": true,
  "file_count": 0,
  "total_size_bytes": 0,
  "created_at": "2026-02-04T12:00:00Z",
  "updated_at": "2026-02-04T12:00:00Z"
}
```

**Auto-Generated:**
- UUID generated automatically
- `is_private` defaults to `true`
- `file_count` starts at 0
- `total_size_bytes` starts at 0

**Notification:**
- "bucket_created" notification sent automatically

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/buckets" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Papers",
    "description": "Academic papers collection"
  }'
```

---

#### 3. Get Bucket

Retrieve a specific bucket.

**Endpoint:** `GET /api/buckets/{bucket_id}`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier

**Response:** 200 OK
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "440e8400-e29b-41d4-a716-446655440000",
  "name": "Research Papers",
  "description": "Academic papers collection",
  "is_private": true,
  "file_count": 15,
  "total_size_bytes": 52428800,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-02-01T14:20:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Bucket not found or doesn't belong to user

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 4. Delete Bucket

Delete a bucket (cascade deletes all files).

**Endpoint:** `DELETE /api/buckets/{bucket_id}`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Bucket deleted"
}
```

**Cascade Deletions:**
- All files in bucket deleted from Supabase Storage
- All file records deleted
- All chunks and embeddings deleted
- All summaries deleted
- All conversations in bucket deleted

**Error Responses:**
- `404 Not Found`: Bucket not found or doesn't belong to user

**cURL Example:**
```bash
curl -X DELETE "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 5. Delete All Buckets

Delete all buckets for user (requires password verification).

**Endpoint:** `POST /api/buckets/delete-all`

**Authentication:** JWT required

**Request Body:**
```json
{
  "password": "CurrentPassword123!"
}
```

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Deleted 5 bucket(s)"
}
```

**Security:**
- Password verification required
- Cascade deletes all files, chunks, summaries, conversations
- Irreversible action

**Error Responses:**
```json
{
  "success": false,
  "message": "Password is incorrect"
}
```

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/buckets/delete-all" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "CurrentPassword123!"
  }'
```

---

#### 6. Get Dashboard Stats

Retrieve dashboard statistics (total buckets, files, storage).

**Endpoint:** `GET /api/buckets/stats/dashboard`

**Authentication:** JWT required

**Response:** 200 OK
```json
{
  "total_buckets": 5,
  "total_files": 127,
  "total_storage_bytes": 524288000
}
```

**Calculations:**
- Aggregates across all user's buckets
- Real-time stats (no caching)

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/buckets/stats/dashboard" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 7. Get Activity Stats

Retrieve activity data for date range (cumulative counts).

**Endpoint:** `GET /api/buckets/stats/activity`

**Authentication:** JWT required

**Query Parameters:**
- `days` (integer, optional): Number of days to look back (default: 30)
- `start_date` (string, optional): Start date (YYYY-MM-DD)
- `end_date` (string, optional): End date (YYYY-MM-DD)

**Response:** 200 OK
```json
{
  "data": [
    {
      "date": "2026-01-05",
      "files": 10,
      "buckets": 2,
      "storage": 15.5
    },
    {
      "date": "2026-01-06",
      "files": 15,
      "buckets": 3,
      "storage": 22.3
    }
  ]
}
```

**Data Fields:**
- `date`: ISO date string (YYYY-MM-DD)
- `files`: Cumulative file count
- `buckets`: Cumulative bucket count
- `storage`: Cumulative storage in MB

**Date Range Logic:**
1. If `start_date` and `end_date` provided: Use those
2. Else if `days` provided: Last N days
3. Else: Default to last 30 days

**cURL Example:**
```bash
# Last 30 days (default)
curl -X GET "https://api.aiveilix.com/api/buckets/stats/activity" \
  -H "Authorization: Bearer <access_token>"

# Last 7 days
curl -X GET "https://api.aiveilix.com/api/buckets/stats/activity?days=7" \
  -H "Authorization: Bearer <access_token>"

# Custom date range
curl -X GET "https://api.aiveilix.com/api/buckets/stats/activity?start_date=2026-01-01&end_date=2026-01-31" \
  -H "Authorization: Bearer <access_token>"
```

---

### Files Endpoints

Base path: `/api/buckets/{bucket_id}`

---

#### 1. Upload File

Upload a file to a bucket (instant response, background processing).

**Endpoint:** `POST /api/buckets/{bucket_id}/upload`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Target bucket identifier

**Request:** `multipart/form-data`
- `file` (file, required): File to upload
- `folder_path` (string, optional): Folder path for organization

**Response:** 200 OK
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "name": "research_paper.pdf",
  "status": "pending",
  "message": "File uploaded! Processing in background. You can chat about it now."
}
```

**Processing Flow:**
1. **Instant Upload**: File saved to Supabase Storage
2. **File Record**: Created with status "pending"
3. **Background Processing**:
   - Status changes to "processing"
   - Text extraction (format-specific)
   - Chunking (150 words, 50-word overlap)
   - Embedding generation (batch OpenAI 3072-dim)
   - Store chunks with embeddings
   - Optional AI summary
   - Status changes to "ready" or "failed"
4. **Notifications**: "file_uploaded" → "file_processed"

**Supported Formats (50+):**

| Category | Formats |
|----------|---------|
| **Images** | JPG, PNG, GIF, BMP, WebP, TIFF (GPT-4o Vision OCR) |
| **Documents** | PDF (PyMuPDF), DOCX (python-docx) |
| **Data** | CSV |
| **Code** | py, js, ts, jsx, tsx, java, c, cpp, cs, go, rs, php, rb, swift, kt |
| **Web** | html, css, scss, sass, vue, svelte |
| **Config** | json, yml, yaml, xml, toml, ini, env |
| **Text** | md, txt, rst, tex, org, adoc |
| **Logs** | log |
| **Other** | sql, sh, bash, ps1, r, m, scala, clj, erl, ex, hs, lua, pl, dart |

**Plan Limits:**

| Plan | Max File Size | Max Documents | Storage |
|------|---------------|---------------|---------|
| Free Trial | 10 MB | 50 | 1 GB |
| Starter | 25 MB | 200 | 3 GB |
| Pro | 50 MB | Unlimited | 10 GB |
| Premium | 100 MB | Unlimited | 50 GB |

**Error Responses:**
- `402 Payment Required`: File size/document/storage limit exceeded
- `404 Not Found`: Bucket not found

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/upload" \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/research_paper.pdf" \
  -F "folder_path=papers/ai"
```

**Python Example:**
```python
import requests

url = "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/upload"
headers = {"Authorization": "Bearer <access_token>"}
files = {"file": open("research_paper.pdf", "rb")}
data = {"folder_path": "papers/ai"}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

---

#### 2. List Files

Get all files in a bucket.

**Endpoint:** `GET /api/buckets/{bucket_id}/files`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier

**Response:** 200 OK
```json
{
  "files": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "bucket_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "research_paper.pdf",
      "original_name": "research_paper.pdf",
      "mime_type": "application/pdf",
      "size_bytes": 5242880,
      "status": "ready",
      "status_message": null,
      "page_count": 15,
      "word_count": 5000,
      "folder_path": "papers/ai",
      "created_at": "2026-02-04T10:30:00Z",
      "updated_at": "2026-02-04T10:32:00Z"
    }
  ],
  "total": 1
}
```

**File Status:**
- `pending`: Uploaded, waiting for processing
- `processing`: Currently being processed
- `ready`: Successfully processed, available for chat
- `failed`: Processing failed (check status_message)

**Sorting:**
- Ordered by `created_at` descending (newest first)

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/files" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 3. Get File Content

Retrieve file content (summary + full text from chunks).

**Endpoint:** `GET /api/buckets/{bucket_id}/files/{file_id}/content`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier
- `file_id` (UUID): File identifier

**Response:** 200 OK
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "name": "research_paper.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 5242880,
  "word_count": 5000,
  "page_count": 15,
  "summary": "This paper explores recent advances in transformer architectures...",
  "content": "Full extracted text from all chunks...",
  "chunk_count": 35
}
```

**Summary Generation:**
- On-demand if not exists
- Uses DeepSeek AI for analysis
- Stored for future requests

**Full File Fallback:**
- If chunks insufficient (<100 chars), fetches full file from storage
- Ensures comprehensive content availability

**Error Responses:**
- `404 Not Found`: File not found or doesn't belong to user/bucket

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/files/660e8400-e29b-41d4-a716-446655440000/content" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 4. Update File Summary

Update or edit the AI-generated summary for a file.

**Endpoint:** `PUT /api/buckets/{bucket_id}/files/{file_id}/summary`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier
- `file_id` (UUID): File identifier

**Request Body:**
```json
{
  "content": "Updated comprehensive analysis of the document..."
}
```

**Response:** 200 OK
```json
{
  "success": true,
  "message": "Summary updated successfully"
}
```

**Behavior:**
- Updates existing summary if exists
- Creates new summary record if doesn't exist

**cURL Example:**
```bash
curl -X PUT "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/files/660e8400-e29b-41d4-a716-446655440000/summary" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated comprehensive analysis..."
  }'
```

---

#### 5. Search Files (Keyword)

Search for keywords across chunks, summaries, and filenames.

**Endpoint:** `GET /api/buckets/{bucket_id}/search`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier

**Query Parameters:**
- `q` (string, required): Search query

**Response:** 200 OK
```json
{
  "query": "transformer architecture",
  "results": [
    {
      "file_id": "660e8400-e29b-41d4-a716-446655440000",
      "file_name": "research_paper.pdf",
      "match_type": "chunk",
      "content": "...discussion of transformer architecture and its applications...",
      "chunk_id": "770e8400-e29b-41d4-a716-446655440000",
      "relevance_score": null
    }
  ],
  "total": 1
}
```

**Search Locations:**
1. **Filenames**: Case-insensitive ILIKE
2. **Chunks**: Full-text search in content
3. **Summaries**: Full-text search in summaries

**Match Types:**
- `filename`: Matched in file name
- `chunk`: Matched in chunk content
- `summary`: Matched in summary

**Snippet Extraction:**
- 100 chars before match
- 100 chars after match
- Fallback to first 200 chars if match not found

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/search?q=transformer%20architecture" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 6. Semantic Search

Search using vector similarity (semantic meaning).

**Endpoint:** `GET /api/buckets/{bucket_id}/semantic-search`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier

**Query Parameters:**
- `q` (string, required): Search query
- `mode` (string, optional): Search mode - "semantic", "keyword", or "hybrid" (default: "hybrid")
- `limit` (integer, optional): Max results (1-50, default: 10)

**Response:** 200 OK
```json
{
  "query": "machine learning optimization techniques",
  "results": [
    {
      "file_id": "660e8400-e29b-41d4-a716-446655440000",
      "file_name": "research_paper.pdf",
      "match_type": "semantic",
      "content": "Advanced optimization strategies for neural networks...",
      "chunk_id": "770e8400-e29b-41d4-a716-446655440000",
      "relevance_score": 0.89
    }
  ],
  "total": 1
}
```

**Search Modes:**

1. **Semantic** (Vector Similarity):
   - Generates embedding for query (OpenAI 3072-dim)
   - Uses pgvector cosine similarity
   - Returns semantically similar content

2. **Keyword** (Text Match):
   - Traditional full-text search
   - PostgreSQL ILIKE
   - Faster but less intelligent

3. **Hybrid** (Recommended):
   - Combines semantic + keyword
   - Deduplicates results
   - Sorts by relevance
   - Best accuracy

**Relevance Score:**
- Range: 0.0 to 1.0
- 1.0 = Perfect match
- 0.5+ = Good relevance
- Semantic mode: Cosine similarity
- Keyword mode: Term frequency

**Performance:**
- IVFFlat index for fast ANN search
- Batch embedding generation
- Configurable result limits

**cURL Example:**
```bash
# Hybrid search (recommended)
curl -X GET "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/semantic-search?q=machine%20learning%20optimization&mode=hybrid&limit=20" \
  -H "Authorization: Bearer <access_token>"

# Semantic only
curl -X GET "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/semantic-search?q=neural%20networks&mode=semantic" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 7. Delete File

Delete a file from a bucket.

**Endpoint:** `DELETE /api/buckets/{bucket_id}/files/{file_id}`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier
- `file_id` (UUID): File identifier

**Response:** 200 OK
```json
{
  "success": true,
  "message": "File deleted"
}
```

**Cascade Deletions:**
- File deleted from Supabase Storage
- File record deleted
- All chunks deleted
- All summaries deleted
- Bucket stats updated

**Error Responses:**
- `404 Not Found`: File not found or doesn't belong to user/bucket

**cURL Example:**
```bash
curl -X DELETE "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/files/660e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <access_token>"
```

---

### Chat Endpoints

Base path: `/api/buckets/{bucket_id}`

---

#### 1. Chat with Bucket

AI-powered chat with your documents (streaming response).

**Endpoint:** `POST /api/buckets/{bucket_id}/chat`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier

**Request Body:**
```json
{
  "message": "What are the main findings in the research papers?",
  "conversation_id": "880e8400-e29b-41d4-a716-446655440000"
}
```

**Request Fields:**
- `message` (string, required): User's question or message
- `conversation_id` (string, optional): UUID of existing conversation (null for new)

**Response:** `text/event-stream` (Server-Sent Events)

**Event Types:**

1. **Searching** (Web search triggered):
```json
{"type": "searching", "keywords": "japan prime minister 2026"}
```

2. **Phase Change** (Extended thinking):
```json
{"type": "phase_change", "phase": "thinking"}
{"type": "phase_change", "phase": "response"}
```

3. **Thinking** (DeepSeek Reasoner reasoning):
```json
{"type": "thinking", "content": "Analyzing the documents..."}
```

4. **Response** (Streaming AI response):
```json
{"type": "response", "content": "Based on the research papers..."}
```

5. **Done** (Final message):
```json
{
  "type": "done",
  "message": "Full AI response text",
  "sources": [
    {
      "type": "document",
      "file_name": "research_paper.pdf",
      "file_id": "660e8400-e29b-41d4-a716-446655440000",
      "confidence": "high"
    },
    {
      "type": "web_search",
      "title": "Japan Prime Minister 2026",
      "url": "https://example.com",
      "domain": "example.com"
    }
  ],
  "conversation_id": "880e8400-e29b-41d4-a716-446655440000",
  "thinking": "Full thinking process..."
}
```

6. **Error**:
```json
{"type": "error", "error": "API quota exceeded"}
```

**AI Model:**
- **Primary**: deepseek-reasoner (with extended thinking)
- **Fallback**: deepseek-chat (if reasoner fails)
- Temperature: 0.7

**Context Building:**
1. **File Inventory**: ALL files (processed + unprocessed)
2. **Summaries**: Comprehensive analyses
3. **Chunks**: Raw content (max 1000 chars each)
4. **Full File Fallback**: If chunks < 500 chars, fetches full file
5. **Web Search**: Auto-triggered for current events
6. **Conversation History**: Last 10 messages

**Source Types:**
- `document`: From uploaded files
- `web_search`: From Google search
- `ai_knowledge`: From AI's training

**Web Search Auto-Detection:**
Triggers for queries like:
- "who is the prime minister of..."
- "what is the weather..."
- "latest news about..."
- "current price of..."

**Extended Thinking:**
- DeepSeek Reasoner shows reasoning process
- Streaming in real-time
- Helps understand AI's analysis

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/chat" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main findings?",
    "conversation_id": null
  }'
```

**JavaScript Example:**
```javascript
const eventSource = new EventSource(
  'https://api.aiveilix.com/api/buckets/550e8400.../chat',
  {
    headers: {
      'Authorization': 'Bearer <access_token>',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: "What are the main findings?",
      conversation_id: null
    })
  }
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'thinking') {
    console.log('Thinking:', data.content);
  } else if (data.type === 'response') {
    console.log('Response:', data.content);
  } else if (data.type === 'done') {
    console.log('Sources:', data.sources);
    eventSource.close();
  }
};
```

---

#### 2. Get Conversations

List all conversations for a bucket.

**Endpoint:** `GET /api/buckets/{bucket_id}/conversations`

**Authentication:** JWT required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier

**Response:** 200 OK
```json
{
  "conversations": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "user_id": "440e8400-e29b-41d4-a716-446655440000",
      "bucket_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Research paper analysis",
      "mode": "full_scan",
      "created_at": "2026-02-04T10:00:00Z",
      "updated_at": "2026-02-04T10:30:00Z"
    }
  ]
}
```

**Sorting:**
- Ordered by `updated_at` descending (most recent first)

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/buckets/550e8400-e29b-41d4-a716-446655440000/conversations" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 3. Get Messages

Retrieve messages for a conversation.

**Endpoint:** `GET /api/conversations/{conversation_id}/messages`

**Authentication:** JWT required

**Path Parameters:**
- `conversation_id` (UUID): Conversation identifier

**Response:** 200 OK
```json
{
  "messages": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "user_id": "440e8400-e29b-41d4-a716-446655440000",
      "conversation_id": "880e8400-e29b-41d4-a716-446655440000",
      "role": "user",
      "content": "What are the main findings?",
      "model_used": null,
      "tokens_used": null,
      "sources": null,
      "metadata": null,
      "created_at": "2026-02-04T10:15:00Z"
    },
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440000",
      "user_id": "440e8400-e29b-41d4-a716-446655440000",
      "conversation_id": "880e8400-e29b-41d4-a716-446655440000",
      "role": "assistant",
      "content": "Based on the research papers, the main findings include...",
      "model_used": "deepseek-reasoner",
      "tokens_used": 1500,
      "sources": [
        {
          "type": "document",
          "file_name": "research_paper.pdf",
          "file_id": "660e8400-e29b-41d4-a716-446655440000"
        }
      ],
      "metadata": {
        "thinking": "Analyzing the documents...",
        "model": "deepseek-reasoner",
        "has_thinking": true
      },
      "created_at": "2026-02-04T10:15:30Z"
    }
  ]
}
```

**Message Roles:**
- `user`: User's message
- `assistant`: AI's response
- `system`: System message (rare)

**Sorting:**
- Ordered by `created_at` ascending (chronological)

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/conversations/880e8400-e29b-41d4-a716-446655440000/messages" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 4. Update Conversation

Update conversation title.

**Endpoint:** `PATCH /api/conversations/{conversation_id}`

**Authentication:** JWT required

**Path Parameters:**
- `conversation_id` (UUID): Conversation identifier

**Request Body:**
```json
{
  "title": "Updated conversation title"
}
```

**Response:** 200 OK
```json
{
  "message": "Conversation updated successfully"
}
```

**Validation:**
- Title cannot be empty

**Error Responses:**
- `400 Bad Request`: Title cannot be empty
- `404 Not Found`: Conversation not found

**cURL Example:**
```bash
curl -X PATCH "https://api.aiveilix.com/api/conversations/880e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated conversation title"
  }'
```

---

#### 5. Delete Conversation

Delete a conversation and all its messages.

**Endpoint:** `DELETE /api/conversations/{conversation_id}`

**Authentication:** JWT required

**Path Parameters:**
- `conversation_id` (UUID): Conversation identifier

**Response:** 200 OK
```json
{
  "message": "Conversation deleted successfully"
}
```

**Cascade Deletions:**
- All messages in conversation deleted
- Conversation record deleted

**Error Responses:**
- `404 Not Found`: Conversation not found

**cURL Example:**
```bash
curl -X DELETE "https://api.aiveilix.com/api/conversations/880e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <access_token>"
```

---

### API Keys Endpoints

Base path: `/api/api-keys`

---

#### 1. Create API Key

Generate a new API key for MCP/CLI access.

**Endpoint:** `POST /api/api-keys`

**Authentication:** JWT required

**Request Body:**
```json
{
  "name": "Cursor Integration",
  "scopes": ["read", "write", "delete"],
  "allowed_buckets": null
}
```

**Request Fields:**
- `name` (string, required): Descriptive name for the key
- `scopes` (array, required): Permissions - ["read", "write", "delete"]
- `allowed_buckets` (array, optional): UUID array or null for all buckets

**Response:** 200 OK
```json
{
  "success": true,
  "message": "API key created successfully",
  "api_key": "aiveilix_sk_live_abc123def456...",
  "key_data": {
    "id": "bb0e8400-e29b-41d4-a716-446655440000",
    "name": "Cursor Integration",
    "key_prefix": "aiveilix_sk_live_abc123...",
    "scopes": ["read", "write", "delete"],
    "allowed_buckets": null,
    "is_active": true,
    "last_used_at": null,
    "request_count": 0,
    "created_at": "2026-02-04T12:00:00Z"
  }
}
```

**CRITICAL SECURITY:**
- **Full key returned ONCE**: Save it immediately
- **Never retrievable**: If lost, must create new key
- **SHA-256 hashed**: Stored irreversibly
- **Prefix only**: First 12 chars stored in plaintext

**Valid Scopes:**
- `read`: View buckets, files, search
- `write`: Upload files, create buckets
- `delete`: Delete files, buckets

**Bucket Restrictions:**
- `null`: All buckets allowed
- `[]`: Specific buckets only (provide UUIDs)

**Notification:**
- "api_key_created" notification sent automatically

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/api-keys" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cursor Integration",
    "scopes": ["read", "write"],
    "allowed_buckets": null
  }'
```

---

#### 2. List API Keys

Get all API keys (never returns full key).

**Endpoint:** `GET /api/api-keys`

**Authentication:** JWT required

**Response:** 200 OK
```json
{
  "keys": [
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440000",
      "name": "Cursor Integration",
      "key_prefix": "aiveilix_sk_live_abc123...",
      "scopes": ["read", "write", "delete"],
      "allowed_buckets": null,
      "is_active": true,
      "last_used_at": "2026-02-04T14:30:00Z",
      "request_count": 127,
      "created_at": "2026-02-04T12:00:00Z"
    }
  ],
  "total": 1
}
```

**Security:**
- Full key NEVER returned in list
- Only prefix shown (first 12 chars)

**Sorting:**
- Ordered by `created_at` descending (newest first)

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/api-keys" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 3. Delete API Key

Revoke/delete an API key.

**Endpoint:** `DELETE /api/api-keys/{key_id}`

**Authentication:** JWT required

**Path Parameters:**
- `key_id` (UUID): API key identifier

**Response:** 200 OK
```json
{
  "success": true,
  "message": "API key deleted successfully"
}
```

**Effects:**
- Key immediately revoked
- All future requests with key rejected
- Usage stats preserved (for audit)

**Error Responses:**
- `404 Not Found`: API key not found

**cURL Example:**
```bash
curl -X DELETE "https://api.aiveilix.com/api/api-keys/bb0e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <access_token>"
```

---

### MCP Endpoints

Base path: `/mcp`

**Authentication:** API Key required (see [API Key Authentication](#api-key-authentication))

---

#### 1. List Buckets (MCP)

List accessible buckets via MCP protocol.

**Endpoint:** `GET /mcp/buckets`

**Authentication:** API Key required

**Response:** 200 OK
```json
{
  "buckets": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Research Papers",
      "description": "Academic papers collection",
      "file_count": 15,
      "total_size_bytes": 52428800,
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

**Filtering:**
- If `allowed_buckets` set in API key: Only those buckets returned
- If `null`: All user's buckets returned

**Rate Limiting:**
- 100 requests/hour per API key

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/mcp/buckets" \
  -H "Authorization: Bearer aiveilix_sk_live_abc123..."
```

---

#### 2. List Files (MCP)

List files in a bucket via MCP.

**Endpoint:** `GET /mcp/buckets/{bucket_id}/files`

**Authentication:** API Key required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier

**Response:** 200 OK
```json
{
  "files": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "name": "research_paper.pdf",
      "status": "ready",
      "status_message": null,
      "word_count": 5000,
      "size_bytes": 5242880,
      "created_at": "2026-02-04T10:30:00Z"
    }
  ],
  "total": 1
}
```

**Access Control:**
- Verifies bucket belongs to API key owner
- Checks `allowed_buckets` restriction

**Error Responses:**
- `403 Forbidden`: API key doesn't have access to this bucket
- `404 Not Found`: Bucket not found

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/mcp/buckets/550e8400-e29b-41d4-a716-446655440000/files" \
  -H "Authorization: Bearer aiveilix_sk_live_abc123..."
```

---

#### 3. Query Bucket (MCP)

Semantic search via MCP.

**Endpoint:** `POST /mcp/buckets/{bucket_id}/query`

**Authentication:** API Key required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier

**Request Body:**
```json
{
  "query": "machine learning optimization",
  "max_results": 10
}
```

**Request Fields:**
- `query` (string, required): Search query
- `max_results` (integer, optional): Max results (default: 10)

**Response:** 200 OK
```json
{
  "results": [
    {
      "file_id": "660e8400-e29b-41d4-a716-446655440000",
      "file_name": "research_paper.pdf",
      "content": "Advanced optimization strategies...",
      "relevance_score": 0.89,
      "chunk_id": "770e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "total": 1,
  "query": "machine learning optimization"
}
```

**Search Strategy:**
1. **Vector Search** (if embedding generation succeeds)
2. **Text Search Fallback** (if vector search fails)

**Relevance Score:**
- Semantic: Cosine similarity (0.0-1.0)
- Text: Term frequency (0.0-1.0)

**Intelligent Fallback:**
- If chunks < 500 chars, fetches full file from storage

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/mcp/buckets/550e8400-e29b-41d4-a716-446655440000/query" \
  -H "Authorization: Bearer aiveilix_sk_live_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning optimization",
    "max_results": 10
  }'
```

---

#### 4. Chat with Bucket (MCP)

AI chat via MCP (non-streaming).

**Endpoint:** `POST /mcp/buckets/{bucket_id}/chat`

**Authentication:** API Key required

**Path Parameters:**
- `bucket_id` (UUID): Bucket identifier

**Request Body:**
```json
{
  "message": "What are the main findings?",
  "conversation_id": null
}
```

**Request Fields:**
- `message` (string, required): User's question
- `conversation_id` (string, optional): UUID of existing conversation

**Response:** 200 OK
```json
{
  "response": "Based on the research papers, the main findings include...",
  "sources": [
    {
      "file_name": "research_paper.pdf",
      "file_id": "660e8400-e29b-41d4-a716-446655440000",
      "type": "analysis",
      "summary_id": "cc0e8400-e29b-41d4-a716-446655440000"
    },
    {
      "file_name": "research_paper.pdf",
      "file_id": "660e8400-e29b-41d4-a716-446655440000",
      "type": "chunk",
      "chunk_id": "770e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "conversation_id": "880e8400-e29b-41d4-a716-446655440000"
}
```

**Source Types:**
- `analysis`: From AI summary
- `chunk`: From chunk content
- `full_file`: From full file (if chunks insufficient)

**AI Model:**
- deepseek-chat (non-streaming for MCP)
- Temperature: 0.7

**Context:**
- Same intelligent context building as web chat
- Full file fallback if chunks < 500 chars

**Error Responses:**
- `429 Too Many Requests`: AI quota exceeded
- `503 Service Unavailable`: AI service not available

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/mcp/buckets/550e8400-e29b-41d4-a716-446655440000/chat" \
  -H "Authorization: Bearer aiveilix_sk_live_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main findings?",
    "conversation_id": null
  }'
```

---

### OAuth Endpoints

Base path: `/api/oauth`

---

#### 1. Create OAuth Client

Register a new OAuth client for third-party access.

**Endpoint:** `POST /api/oauth/clients`

**Authentication:** JWT required

**Request Body:**
```json
{
  "name": "My ChatGPT Integration",
  "redirect_uris": ["https://chat.openai.com/aip/callback"],
  "scopes": ["read", "write", "query", "chat"]
}
```

**Request Fields:**
- `name` (string, required): Client name
- `redirect_uris` (array, required): Allowed redirect URIs
- `scopes` (array, required): Requested scopes

**Response:** 200 OK
```json
{
  "client_id": "dd0e8400-e29b-41d4-a716-446655440000",
  "client_secret": "secret_abc123def456...",
  "name": "My ChatGPT Integration",
  "redirect_uris": ["https://chat.openai.com/aip/callback"],
  "scopes": ["read", "write", "query", "chat"],
  "created_at": "2026-02-04T12:00:00Z"
}
```

**CRITICAL SECURITY:**
- **Client secret returned ONCE**: Save immediately
- **Never retrievable**: If lost, must create new client
- **SHA-256 hashed**: Stored irreversibly

**Valid Scopes:**
- `read`: View buckets, files, search
- `write`: Upload files, create buckets
- `query`: Semantic search
- `chat`: AI chat capabilities
- `full`: All permissions

**cURL Example:**
```bash
curl -X POST "https://api.aiveilix.com/api/oauth/clients" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My ChatGPT Integration",
    "redirect_uris": ["https://chat.openai.com/aip/callback"],
    "scopes": ["read", "write", "query", "chat"]
  }'
```

---

#### 2. List OAuth Clients

Get all OAuth clients (never returns secret).

**Endpoint:** `GET /api/oauth/clients`

**Authentication:** JWT required

**Response:** 200 OK
```json
[
  {
    "client_id": "dd0e8400-e29b-41d4-a716-446655440000",
    "name": "My ChatGPT Integration",
    "redirect_uris": ["https://chat.openai.com/aip/callback"],
    "scopes": ["read", "write", "query", "chat"],
    "is_active": true,
    "created_at": "2026-02-04T12:00:00Z"
  }
]
```

**Security:**
- Client secret NEVER returned in list

**cURL Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/oauth/clients" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 3. Delete OAuth Client

Revoke an OAuth client.

**Endpoint:** `DELETE /api/oauth/clients/{client_id}`

**Authentication:** JWT required

**Path Parameters:**
- `client_id` (UUID): OAuth client identifier

**Response:** 200 OK
```json
{
  "success": true,
  "message": "OAuth client revoked successfully"
}
```

**Effects:**
- Client immediately revoked
- All access tokens issued to client invalidated
- All refresh tokens revoked

**Error Responses:**
- `404 Not Found`: OAuth client not found

**cURL Example:**
```bash
curl -X DELETE "https://api.aiveilix.com/api/oauth/clients/dd0e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <access_token>"
```

---

### Notifications Endpoints

Base path: `/api/notifications`

---

#### 1. Get Notifications

Retrieve all notifications for the current user.

**Endpoint:** `GET /api/notifications`

**Authentication:** JWT required

**Query Parameters:**
- `limit` (integer, optional): Max results (default: 50)
- `offset` (integer, optional): Pagination offset (default: 0)
- `unread_only` (boolean, optional): Only unread (default: false)

**Response:** 200 OK
```json
{
  "notifications": [
    {
      "id": "ee0e8400-e29b-41d4-a716-446655440000",
      "user_id": "440e8400-e29b-41d4-a716-446655440000",
      "type": "file_processed",
      "title": "File Ready",
      "message": "research_paper.pdf has been processed successfully",
      "icon": "✅",
      "metadata": {
        "file_id": "660e8400-e29b-41d4-a716-446655440000",
        "file_name": "research_paper.pdf",
        "bucket_id": "550e8400-e29b-41d4-a716-446655440000"
      },
      "action_url": "/buckets/550e8400-e29b-41d4-a716-446655440000",
      "is_read": false,
      "read_at": null,
      "created_at": "2026-02-04T10:32:00Z",
      "updated_at": "2026-02-04T10:32:00Z"
    }
  ],
  "unread_count": 5,
  "total": 1
}
```

**Notification Types:**
- `login`: "Welcome back!"
- `file_uploaded`: "File {name} uploaded"
- `file_processed`: "File {name} ready"
- `bucket_created`: "Bucket {name} created"
- `api_key_created`: "API key {name} created"

**Sorting:**
- Ordered by `created_at` descending (newest first)

**cURL Example:**
```bash
# All notifications
curl -X GET "https://api.aiveilix.com/api/notifications" \
  -H "Authorization: Bearer <access_token>"

# Unread only
curl -X GET "https://api.aiveilix.com/api/notifications?unread_only=true" \
  -H "Authorization: Bearer <access_token>"

# Pagination
curl -X GET "https://api.aiveilix.com/api/notifications?limit=20&offset=40" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 2. Mark as Read

Mark a notification as read.

**Endpoint:** `PATCH /api/notifications/{notification_id}/read`

**Authentication:** JWT required

**Path Parameters:**
- `notification_id` (UUID): Notification identifier

**Response:** 200 OK
```json
{
  "message": "Notification marked as read",
  "notification": {
    "id": "ee0e8400-e29b-41d4-a716-446655440000",
    "is_read": true,
    "read_at": "2026-02-04T14:00:00Z"
  }
}
```

**Error Responses:**
- `404 Not Found`: Notification not found

**cURL Example:**
```bash
curl -X PATCH "https://api.aiveilix.com/api/notifications/ee0e8400-e29b-41d4-a716-446655440000/read" \
  -H "Authorization: Bearer <access_token>"
```

---

#### 3. Mark All as Read

Mark all notifications as read.

**Endpoint:** `PATCH /api/notifications/mark-all-read`

**Authentication:** JWT required

**Response:** 200 OK
```json
{
  "message": "All notifications marked as read",
  "count": 5
}
```

**cURL Example:**
```bash
curl -X PATCH "https://api.aiveilix.com/api/notifications/mark-all-read" \
  -H "Authorization: Bearer <access_token>"
```

---

## Rate Limits

AIveilix implements multiple rate limiting strategies to ensure fair usage and system stability.

### MCP Endpoints

**Limit:** 100 requests/hour per API key

**Applies to:**
- `/mcp/buckets`
- `/mcp/buckets/{bucket_id}/files`
- `/mcp/buckets/{bucket_id}/query`
- `/mcp/buckets/{bucket_id}/chat`

**Implementation:**
- Sliding window rate limiting
- In-memory tracking per API key
- Resets every hour

**Error Response:** 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Try again in 30 minutes."
}
```

**Headers (future):**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704067200
```

---

### Plan-Based Limits

**Daily API Calls:**

| Plan | API Calls/Day |
|------|---------------|
| Free Trial | 50 |
| Starter | 100 |
| Pro | 1,000 |
| Premium | 5,000 |

**Applies to:**
- All authenticated endpoints
- Checked before processing
- Resets daily at midnight UTC

**Error Response:** 429 Too Many Requests
```json
{
  "error": "api_rate_limit",
  "message": "Daily API limit reached (50 calls/day). Upgrade your plan for more API calls.",
  "upgrade_required": true
}
```

---

### AI Service Limits

**DeepSeek API:**
- Quota managed by DeepSeek
- May return 429 if quota exceeded

**OpenAI Embeddings:**
- Batch limit: 2048 inputs per request
- Rate limits managed by OpenAI

**Error Handling:**
- Automatic retry with exponential backoff
- Graceful degradation (fallback strategies)

---

## Pricing Plans

AIveilix offers 4 pricing tiers with increasing limits and features.

### Plan Comparison

| Feature | Free Trial | Starter | Pro | Premium |
|---------|-----------|---------|-----|---------|
| **Storage** | 1 GB | 3 GB | 10 GB | 50 GB |
| **Max Documents** | 50 | 200 | Unlimited | Unlimited |
| **Max File Size** | 10 MB | 25 MB | 50 MB | 100 MB |
| **API Calls/Day** | 50 | 100 | 1,000 | 5,000 |
| **MCP Access** | ✅ | ✅ | ✅ | ✅ |
| **Vector Search** | ✅ | ✅ | ✅ | ✅ |
| **AI Chat** | ✅ | ✅ | ✅ | ✅ |
| **Web Search** | ✅ | ✅ | ✅ | ✅ |
| **Extended Thinking** | ✅ | ✅ | ✅ | ✅ |
| **OAuth2** | ❌ | ✅ | ✅ | ✅ |
| **Priority Support** | ❌ | ❌ | ✅ | ✅ |
| **SLA** | ❌ | ❌ | ❌ | 99.9% |

---

### Detailed Plan Limits

#### Free Trial

**Storage:** 1 GB
**Documents:** 50 files
**File Size:** 10 MB per file
**API Calls:** 50/day

**Duration:** 14 days trial
**After Trial:** Expired (read-only access)

**Ideal for:**
- Testing AIveilix
- Small personal projects
- Proof of concept

**Upgrade Prompt:**
- Shown when approaching limits (80%+)
- Required when limits exceeded

---

#### Starter

**Storage:** 3 GB
**Documents:** 200 files
**File Size:** 25 MB per file
**API Calls:** 100/day

**Price:** $9/month (billed monthly)

**Ideal for:**
- Freelancers
- Small teams
- Side projects

**Features:**
- OAuth2 support
- Email support
- All AI features

---

#### Pro

**Storage:** 10 GB
**Documents:** Unlimited
**File Size:** 50 MB per file
**API Calls:** 1,000/day

**Price:** $29/month (billed monthly)

**Ideal for:**
- Growing teams
- Professional use
- Medium-sized projects

**Features:**
- Priority support
- Advanced analytics
- Custom integrations

---

#### Premium

**Storage:** 50 GB
**Documents:** Unlimited
**File Size:** 100 MB per file
**API Calls:** 5,000/day

**Price:** $99/month (billed monthly)

**Ideal for:**
- Enterprises
- Large teams
- Mission-critical applications

**Features:**
- 99.9% SLA
- Dedicated support
- Custom deployment options
- Advanced security features

---

### Usage Monitoring

**Get Usage Summary:**

**Endpoint:** `GET /api/usage/summary` (future endpoint)

**Response:**
```json
{
  "plan": "pro",
  "usage": {
    "storage": {
      "used_bytes": 5368709120,
      "limit_bytes": 10737418240,
      "used_gb": 5.0,
      "limit_gb": 10.0,
      "percentage": 50.0
    },
    "documents": {
      "count": 500,
      "limit": -1,
      "percentage": 0
    },
    "api_calls": {
      "today": 250,
      "limit": 1000,
      "percentage": 25.0
    },
    "max_file_size_mb": 50
  }
}
```

**Usage Alerts:**
- **80% threshold**: Warning email sent
- **90% threshold**: Urgent upgrade prompt
- **100% threshold**: Uploads blocked, upgrade required

---

## Error Handling

AIveilix uses standard HTTP status codes and consistent error formats.

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 402 | Payment Required | Plan limit exceeded, upgrade needed |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error (contact support) |
| 503 | Service Unavailable | Service temporarily down |

---

### Error Response Format

**Standard Error:**
```json
{
  "detail": "Error message description"
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Plan Limit Error:**
```json
{
  "detail": {
    "error": "storage_limit",
    "message": "Storage limit reached (3GB). Upgrade your plan for more storage.",
    "upgrade_required": true
  }
}
```

---

### Common Errors

#### 401 Unauthorized

**Cause:** Missing or invalid token/API key

**Solutions:**
- Include `Authorization: Bearer <token>` header
- Check token hasn't expired (60 min for access tokens)
- Verify API key is active and not revoked
- Ensure API key format is correct

**Example:**
```bash
curl -X GET "https://api.aiveilix.com/api/buckets" \
  -H "Authorization: Bearer <valid_token>"
```

---

#### 402 Payment Required

**Cause:** Plan limit exceeded

**Limit Types:**
- `storage_limit`: Storage quota exceeded
- `document_limit`: Max documents reached
- `file_size_limit`: File too large
- `api_rate_limit`: Daily API calls exceeded

**Solutions:**
- Upgrade to higher plan
- Delete unused files/buckets
- Wait until next day (for API rate limit)

**Response:**
```json
{
  "detail": {
    "error": "storage_limit",
    "message": "Storage limit reached (3GB). Upgrade your plan for more storage.",
    "upgrade_required": true
  }
}
```

---

#### 404 Not Found

**Cause:** Resource doesn't exist or doesn't belong to user

**Common Scenarios:**
- Bucket ID invalid or deleted
- File ID invalid or deleted
- Conversation ID invalid
- Cross-user access attempt

**Solutions:**
- Verify UUID format is correct
- Check resource belongs to authenticated user
- Confirm resource wasn't deleted

---

#### 429 Too Many Requests

**Cause:** Rate limit exceeded

**Types:**
- MCP: 100 requests/hour
- API: Daily limit per plan

**Solutions:**
- Wait for rate limit reset
- Upgrade plan for higher limits
- Optimize request frequency

**Response:**
```json
{
  "detail": "Rate limit exceeded. Try again in 30 minutes."
}
```

---

## Code Examples

### Python Client

```python
import requests
import json

class AIveilixClient:
    def __init__(self, api_key=None, access_token=None):
        self.base_url = "https://api.aiveilix.com"
        self.headers = {}

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        elif access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"

    def login(self, email, password):
        """Authenticate and get access token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.headers["Authorization"] = f"Bearer {data['session']['access_token']}"
        return data

    def list_buckets(self):
        """List all buckets"""
        response = requests.get(
            f"{self.base_url}/api/buckets",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_bucket(self, name, description=""):
        """Create a new bucket"""
        response = requests.post(
            f"{self.base_url}/api/buckets",
            headers=self.headers,
            json={"name": name, "description": description}
        )
        response.raise_for_status()
        return response.json()

    def upload_file(self, bucket_id, file_path, folder_path=None):
        """Upload a file to a bucket"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {}
            if folder_path:
                data["folder_path"] = folder_path

            response = requests.post(
                f"{self.base_url}/api/buckets/{bucket_id}/upload",
                headers=self.headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()

    def semantic_search(self, bucket_id, query, mode="hybrid", limit=10):
        """Perform semantic search"""
        response = requests.get(
            f"{self.base_url}/api/buckets/{bucket_id}/semantic-search",
            headers=self.headers,
            params={"q": query, "mode": mode, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    def chat(self, bucket_id, message, conversation_id=None):
        """Chat with AI (non-streaming)"""
        response = requests.post(
            f"{self.base_url}/api/buckets/{bucket_id}/chat",
            headers=self.headers,
            json={
                "message": message,
                "conversation_id": conversation_id
            },
            stream=True
        )
        response.raise_for_status()

        # Process streaming response
        full_response = ""
        sources = []
        thinking = ""

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = json.loads(line[6:])

                    if data['type'] == 'thinking':
                        thinking += data['content']
                    elif data['type'] == 'response':
                        full_response += data['content']
                    elif data['type'] == 'done':
                        sources = data['sources']
                        conversation_id = data['conversation_id']

        return {
            "response": full_response,
            "sources": sources,
            "thinking": thinking,
            "conversation_id": conversation_id
        }

# Usage Example
client = AIveilixClient()
client.login("user@example.com", "password123")

# Create bucket
bucket = client.create_bucket("Research Papers", "AI research collection")

# Upload file
upload_result = client.upload_file(
    bucket['id'],
    "/path/to/paper.pdf",
    folder_path="ai/transformers"
)

# Search
results = client.semantic_search(
    bucket['id'],
    "transformer architecture",
    mode="hybrid"
)

# Chat
chat_response = client.chat(
    bucket['id'],
    "What are the main findings in the papers?"
)
print(chat_response['response'])
print("Sources:", chat_response['sources'])
```

---

### JavaScript/TypeScript Client

```typescript
interface AIveilixClientConfig {
  apiKey?: string;
  accessToken?: string;
  baseUrl?: string;
}

class AIveilixClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(config: AIveilixClientConfig = {}) {
    this.baseUrl = config.baseUrl || 'https://api.aiveilix.com';
    this.headers = {};

    if (config.apiKey) {
      this.headers['Authorization'] = `Bearer ${config.apiKey}`;
    } else if (config.accessToken) {
      this.headers['Authorization'] = `Bearer ${config.accessToken}`;
    }
  }

  async login(email: string, password: string) {
    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) throw new Error('Login failed');

    const data = await response.json();
    this.headers['Authorization'] = `Bearer ${data.session.access_token}`;
    return data;
  }

  async listBuckets() {
    const response = await fetch(`${this.baseUrl}/api/buckets`, {
      headers: this.headers
    });

    if (!response.ok) throw new Error('Failed to list buckets');
    return response.json();
  }

  async createBucket(name: string, description: string = '') {
    const response = await fetch(`${this.baseUrl}/api/buckets`, {
      method: 'POST',
      headers: { ...this.headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description })
    });

    if (!response.ok) throw new Error('Failed to create bucket');
    return response.json();
  }

  async uploadFile(bucketId: string, file: File, folderPath?: string) {
    const formData = new FormData();
    formData.append('file', file);
    if (folderPath) formData.append('folder_path', folderPath);

    const response = await fetch(
      `${this.baseUrl}/api/buckets/${bucketId}/upload`,
      {
        method: 'POST',
        headers: this.headers,
        body: formData
      }
    );

    if (!response.ok) throw new Error('Failed to upload file');
    return response.json();
  }

  async semanticSearch(
    bucketId: string,
    query: string,
    mode: 'semantic' | 'keyword' | 'hybrid' = 'hybrid',
    limit: number = 10
  ) {
    const params = new URLSearchParams({
      q: query,
      mode,
      limit: limit.toString()
    });

    const response = await fetch(
      `${this.baseUrl}/api/buckets/${bucketId}/semantic-search?${params}`,
      { headers: this.headers }
    );

    if (!response.ok) throw new Error('Search failed');
    return response.json();
  }

  async chat(bucketId: string, message: string, conversationId?: string) {
    const response = await fetch(
      `${this.baseUrl}/api/buckets/${bucketId}/chat`,
      {
        method: 'POST',
        headers: { ...this.headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, conversation_id: conversationId })
      }
    );

    if (!response.ok) throw new Error('Chat failed');

    // Process streaming response
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    let fullResponse = '';
    let sources = [];
    let thinking = '';
    let finalConversationId = '';

    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.substring(6));

          if (data.type === 'thinking') {
            thinking += data.content;
          } else if (data.type === 'response') {
            fullResponse += data.content;
          } else if (data.type === 'done') {
            sources = data.sources;
            finalConversationId = data.conversation_id;
          }
        }
      }
    }

    return {
      response: fullResponse,
      sources,
      thinking,
      conversation_id: finalConversationId
    };
  }
}

// Usage Example
const client = new AIveilixClient();
await client.login('user@example.com', 'password123');

// Create bucket
const bucket = await client.createBucket('Research Papers', 'AI research');

// Upload file
const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
const file = fileInput.files![0];
await client.uploadFile(bucket.id, file, 'ai/transformers');

// Search
const results = await client.semanticSearch(
  bucket.id,
  'transformer architecture',
  'hybrid'
);

// Chat
const chatResponse = await client.chat(
  bucket.id,
  'What are the main findings?'
);
console.log(chatResponse.response);
console.log('Sources:', chatResponse.sources);
```

---

## Appendix

### Webhook Support (Future)

Coming soon: Real-time webhooks for events like file processing completion, quota alerts, etc.

### GraphQL API (Future)

Coming soon: GraphQL endpoint for flexible querying.

### SDKs

Official SDKs planned for:
- Python
- JavaScript/TypeScript
- Go
- Ruby

---

## Support

**Documentation:** https://docs.aiveilix.com
**Email:** support@aiveilix.com
**GitHub:** https://github.com/aiveilix
**Discord:** https://discord.gg/aiveilix

---

**Last Updated:** February 4, 2026
**API Version:** v1
**Documentation Version:** 1.0.0

---

Made with ❤️ by AIveilix Team
