# Aiveilix — API Endpoints

> This document describes every FastAPI endpoint in Aiveilix. Each endpoint includes its method, path, purpose, request body, and response example.

---

## Base URL

```
https://api.aiveilix.com/v1
```

All protected endpoints require a valid JWT access token in the Authorization header:

```
Authorization: Bearer {access_token}
```

---

## Auth Endpoints

### `POST /auth/register`

Creates a new user account with email and password.

**Request:**
```json
{
  "full_name": "John Doe",
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

**Response:**
```json
{
  "message": "Account created. Please check your email to verify your account."
}
```

---

### `POST /auth/verify-email`

Verifies the user's email address using the token sent in the verification email.

**Request:**
```json
{
  "token": "email_verification_token_here"
}
```

**Response:**
```json
{
  "message": "Email verified successfully."
}
```

---

### `POST /auth/login`

Logs in with email and password. Returns JWT access token and refresh token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

**Response (no 2FA):**
```json
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "token_type": "bearer"
}
```

**Response (2FA enabled):**
```json
{
  "requires_2fa": true,
  "temp_token": "temp_token_here"
}
```

---

### `POST /auth/2fa/verify`

Verifies the TOTP code during login when 2FA is enabled.

**Request:**
```json
{
  "temp_token": "temp_token_here",
  "code": "123456"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "token_type": "bearer"
}
```

---

### `POST /auth/2fa/enable`

Enables two-factor authentication for the user. Returns a QR code URI.

**Request:** none (uses JWT from header)

**Response:**
```json
{
  "secret": "BASE32SECRET",
  "qr_uri": "otpauth://totp/Aiveilix:user@example.com?secret=BASE32SECRET&issuer=Aiveilix"
}
```

---

### `POST /auth/2fa/confirm`

Confirms 2FA setup by verifying the first TOTP code after scanning the QR code.

**Request:**
```json
{
  "code": "123456"
}
```

**Response:**
```json
{
  "message": "Two-factor authentication enabled successfully."
}
```

---

### `POST /auth/2fa/disable`

Disables two-factor authentication. Requires current TOTP code for confirmation.

**Request:**
```json
{
  "code": "123456"
}
```

**Response:**
```json
{
  "message": "Two-factor authentication disabled successfully."
}
```

---

### `POST /auth/refresh`

Issues a new access token using a valid refresh token.

**Request:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Response:**
```json
{
  "access_token": "new_jwt_token_here",
  "token_type": "bearer"
}
```

---

### `POST /auth/logout`

Logs out the user. Blacklists the JWT and deletes the refresh token from Redis.

**Request:** none (uses JWT from header)

**Response:**
```json
{
  "message": "Logged out successfully."
}
```

---

### `POST /auth/forgot-password`

Sends a password reset email to the user.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If this email exists, a password reset link has been sent."
}
```

---

### `POST /auth/reset-password`

Resets the user's password using the token from the reset email.

**Request:**
```json
{
  "token": "reset_token_here",
  "new_password": "NewStrongPassword123!"
}
```

**Response:**
```json
{
  "message": "Password reset successfully."
}
```

---

### `POST /auth/google`

Handles Google OAuth callback and returns JWT tokens.

**Request:**
```json
{
  "code": "google_auth_code_here",
  "redirect_uri": "https://aiveilix.com/auth/callback/google"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "token_type": "bearer",
  "is_new_user": true
}
```

---

### `POST /auth/github`

Handles GitHub OAuth callback and returns JWT tokens.

**Request:**
```json
{
  "code": "github_auth_code_here",
  "redirect_uri": "https://aiveilix.com/auth/callback/github"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "token_type": "bearer",
  "is_new_user": true
}
```

---

## User and Profile Endpoints

### `GET /user/profile`

Returns the current user's profile.

**Response:**
```json
{
  "user_id": "u_abc123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": "https://r2.aiveilix.com/avatars/u_abc123.jpg",
  "bio": "AI enthusiast",
  "theme": "dark",
  "language": "en",
  "timezone": "Asia/Tokyo",
  "two_factor_enabled": true
}
```

---

### `PUT /user/profile`

Updates the current user's profile.

**Request:**
```json
{
  "full_name": "John Doe Updated",
  "bio": "Builder and AI enthusiast",
  "theme": "light",
  "language": "en",
  "timezone": "Asia/Tokyo"
}
```

**Response:**
```json
{
  "message": "Profile updated successfully."
}
```

---

### `PUT /user/avatar`

Uploads a new profile picture.

**Request:** multipart/form-data with image file

**Response:**
```json
{
  "avatar_url": "https://r2.aiveilix.com/avatars/u_abc123.jpg"
}
```

---

### `PUT /user/password`

Changes the user's password.

**Request:**
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

**Response:**
```json
{
  "message": "Password changed successfully."
}
```

---

### `DELETE /user/account`

Permanently deletes the user's account and all associated data.

**Request:**
```json
{
  "password": "CurrentPassword123!"
}
```

**Response:**
```json
{
  "message": "Account deleted successfully."
}
```

---

## Bucket Endpoints

### `GET /buckets`

Returns all buckets for the current user.

**Response:**
```json
{
  "buckets": [
    {
      "bucket_id": "b_xyz789",
      "name": "Company Research",
      "description": "All company research documents",
      "color": "#3B82F6",
      "icon": "folder",
      "storage_used": 52428800,
      "files_count": 12,
      "created_at": "2026-03-10T09:00:00Z"
    }
  ]
}
```

---

### `POST /buckets`

Creates a new bucket.

**Request:**
```json
{
  "name": "Company Research",
  "description": "All company research documents",
  "color": "#3B82F6",
  "icon": "folder"
}
```

**Response:**
```json
{
  "bucket_id": "b_xyz789",
  "name": "Company Research",
  "mcp_url": "https://mcp.aiveilix.com/bucket/tok_abc123xyz",
  "created_at": "2026-03-10T09:00:00Z"
}
```

---

### `GET /buckets/{bucket_id}`

Returns full details of a specific bucket.

**Response:**
```json
{
  "bucket_id": "b_xyz789",
  "name": "Company Research",
  "description": "All company research documents",
  "color": "#3B82F6",
  "storage_used": 52428800,
  "files_count": 12,
  "mcp_url": "https://mcp.aiveilix.com/bucket/tok_abc123xyz",
  "created_at": "2026-03-10T09:00:00Z"
}
```

---

### `PUT /buckets/{bucket_id}`

Updates a bucket's name, description, color, or icon.

**Request:**
```json
{
  "name": "Updated Bucket Name",
  "description": "Updated description",
  "color": "#10B981"
}
```

**Response:**
```json
{
  "message": "Bucket updated successfully."
}
```

---

### `DELETE /buckets/{bucket_id}`

Deletes a bucket and all its files and embeddings.

**Response:**
```json
{
  "message": "Bucket deleted successfully."
}
```

---

### `GET /buckets/{bucket_id}/mcp-url`

Returns the MCP URL and token for a bucket.

**Response:**
```json
{
  "mcp_url": "https://mcp.aiveilix.com/bucket/tok_abc123xyz",
  "account_mcp_url": "https://mcp.aiveilix.com/account/acc_tok_789",
  "last_used_at": "2026-03-20T14:00:00Z"
}
```

---

### `POST /buckets/{bucket_id}/mcp-url/regenerate`

Regenerates the MCP token for a bucket. The old token is immediately revoked.

**Response:**
```json
{
  "mcp_url": "https://mcp.aiveilix.com/bucket/tok_new123xyz",
  "message": "MCP URL regenerated. The old URL is no longer valid."
}
```

---

### `POST /buckets/{bucket_id}/mcp-url/revoke`

Revokes the MCP token for a bucket without generating a new one.

**Response:**
```json
{
  "message": "MCP access revoked successfully."
}
```

---

## File Endpoints

### `POST /buckets/{bucket_id}/files`

Uploads one or more files to a bucket. Supports bulk upload.

**Request:** multipart/form-data with one or more files

**Response:**
```json
{
  "files": [
    {
      "file_id": "f_abc123",
      "name": "company-report.pdf",
      "status": "processing"
    }
  ]
}
```

---

### `GET /buckets/{bucket_id}/files`

Lists all files in a bucket.

**Response:**
```json
{
  "files": [
    {
      "file_id": "f_abc123",
      "name": "company-report.pdf",
      "type": "pdf",
      "size": 2048000,
      "page_count": 10,
      "status": "ready",
      "created_at": "2026-03-15T08:00:00Z"
    }
  ]
}
```

---

### `GET /buckets/{bucket_id}/files/{file_id}`

Returns full details of a specific file.

**Response:**
```json
{
  "file_id": "f_abc123",
  "name": "company-report.pdf",
  "type": "pdf",
  "size": 2048000,
  "page_count": 10,
  "status": "ready",
  "r2_path": "raw/f_abc123/company-report.pdf",
  "layout_json_path": "layouts/f_abc123/layout.json",
  "version": 1,
  "created_at": "2026-03-15T08:00:00Z"
}
```

---

### `DELETE /buckets/{bucket_id}/files/{file_id}`

Deletes a file and all its embeddings from Qdrant.

**Response:**
```json
{
  "message": "File deleted successfully."
}
```

---

### `GET /buckets/{bucket_id}/files/{file_id}/summary`

Returns the AI-generated summary for a specific file.

**Response:**
```json
{
  "file_id": "f_abc123",
  "file_name": "company-report.pdf",
  "summary": "This report covers Q3 financial performance. Total revenue grew 23% driven by Asia-Pacific expansion."
}
```

---

### `GET /buckets/{bucket_id}/files/{file_id}/layout`

Returns the full Layout JSON Map for a specific file.

**Response:**
```json
{
  "file_id": "f_abc123",
  "total_pages": 10,
  "pages": [
    {
      "page": 1,
      "blocks": [
        {
          "id": "text_1",
          "type": "heading",
          "content": "Q3 Financial Report",
          "x": 50,
          "y": 80
        },
        {
          "id": "img_1",
          "type": "bar_chart",
          "description": "A blue bar chart showing monthly revenue growth.",
          "text_inside": "July: $200k, August: $230k, September: $260k",
          "x": 50,
          "y": 500
        }
      ]
    }
  ]
}
```

---

### `GET /buckets/{bucket_id}/files/{file_id}/chunks`

Lists all chunks for a specific file.

**Response:**
```json
{
  "chunks": [
    {
      "chunk_id": "chunk_001",
      "page": 1,
      "content": "Total revenue increased by 23% this quarter.",
      "token_count": 24,
      "nearby_image_id": "img_1"
    }
  ]
}
```

---

## Category Endpoints

### `GET /buckets/{bucket_id}/categories`

Lists all categories in a bucket.

**Response:**
```json
{
  "categories": [
    {
      "category_id": "cat_001",
      "name": "Financial Reports",
      "color": "#3B82F6",
      "files_count": 5
    }
  ]
}
```

---

### `POST /buckets/{bucket_id}/categories`

Creates a new category in a bucket.

**Request:**
```json
{
  "name": "Financial Reports",
  "color": "#3B82F6"
}
```

**Response:**
```json
{
  "category_id": "cat_001",
  "name": "Financial Reports",
  "color": "#3B82F6"
}
```

---

### `DELETE /buckets/{bucket_id}/categories/{category_id}`

Deletes a category. Files in the category are moved to uncategorized.

**Response:**
```json
{
  "message": "Category deleted successfully."
}
```

---

## Search and Query Endpoints

### `POST /buckets/{bucket_id}/search`

Performs semantic hybrid search across all documents in the bucket using RAG, Layout JSON, and BGE Reranker.

**Request:**
```json
{
  "query": "What was the revenue in August?",
  "top_k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "chunk_id": "chunk_001",
      "file_name": "company-report.pdf",
      "page": 1,
      "content": "Total revenue increased by 23% this quarter.",
      "nearby_image": {
        "description": "A blue bar chart showing monthly revenue growth.",
        "text_inside": "July: $200k, August: $230k, September: $260k"
      },
      "score": 0.97
    }
  ]
}
```

---

### `POST /buckets/{bucket_id}/query`

Asks a natural language question and returns a full AI-generated answer with sources.

**Request:**
```json
{
  "question": "What was the revenue in August?",
  "conversation_id": "conv_001"
}
```

**Response:**
```json
{
  "answer": "Revenue in August was $230,000, representing a 15% increase from July's $200,000.",
  "sources": [
    {
      "file_name": "company-report.pdf",
      "page": 1,
      "chunk_id": "chunk_001"
    }
  ]
}
```

---

## Conversation and Message Endpoints

### `GET /buckets/{bucket_id}/conversations`

Lists all conversations in a bucket. Maximum 20 per bucket.

**Response:**
```json
{
  "conversations": [
    {
      "conversation_id": "conv_001",
      "title": "Revenue Analysis Q3",
      "created_at": "2026-03-20T10:00:00Z",
      "updated_at": "2026-03-20T11:00:00Z"
    }
  ]
}
```

---

### `POST /buckets/{bucket_id}/conversations`

Creates a new conversation in a bucket.

**Request:**
```json
{
  "title": "Revenue Analysis Q3"
}
```

**Response:**
```json
{
  "conversation_id": "conv_001",
  "title": "Revenue Analysis Q3",
  "created_at": "2026-03-20T10:00:00Z"
}
```

---

### `DELETE /buckets/{bucket_id}/conversations/{conversation_id}`

Deletes a conversation and all its messages.

**Response:**
```json
{
  "message": "Conversation deleted successfully."
}
```

---

### `GET /buckets/{bucket_id}/conversations/{conversation_id}/messages`

Returns all messages in a conversation.

**Response:**
```json
{
  "messages": [
    {
      "message_id": "msg_001",
      "role": "user",
      "content": "What was the revenue in August?",
      "created_at": "2026-03-20T10:01:00Z"
    },
    {
      "message_id": "msg_002",
      "role": "assistant",
      "content": "Revenue in August was $230,000.",
      "chunks_used": ["chunk_001", "chunk_002"],
      "created_at": "2026-03-20T10:01:05Z"
    }
  ]
}
```

---

### `POST /buckets/{bucket_id}/conversations/{conversation_id}/messages`

Sends a message in a conversation and gets an AI response.

**Request:**
```json
{
  "content": "What was the revenue in August?"
}
```

**Response:**
```json
{
  "message_id": "msg_002",
  "role": "assistant",
  "content": "Revenue in August was $230,000, representing a 15% increase from July.",
  "sources": [
    {
      "file_name": "company-report.pdf",
      "page": 1
    }
  ],
  "created_at": "2026-03-20T10:01:05Z"
}
```

---

## Notification Endpoints

### `GET /notifications`

Returns all notifications for the current user.

**Response:**
```json
{
  "notifications": [
    {
      "notification_id": "n_001",
      "type": "success",
      "title": "File Ready",
      "message": "company-report.pdf has been processed and is ready.",
      "is_read": false,
      "created_at": "2026-03-20T10:00:00Z"
    }
  ]
}
```

---

### `PUT /notifications/read-all`

Marks all notifications as read.

**Response:**
```json
{
  "message": "All notifications marked as read."
}
```

---

### `DELETE /notifications/{notification_id}`

Deletes a specific notification.

**Response:**
```json
{
  "message": "Notification deleted successfully."
}
```

---

## Billing Endpoints

### `GET /billing/plan`

Returns the current user's plan and usage stats.

**Response:**
```json
{
  "plan": "individual",
  "status": "active",
  "storage_used": 104857600,
  "storage_limit": 10737418240,
  "current_period_end": "2026-04-27T00:00:00Z"
}
```

---

### `POST /billing/upgrade`

Upgrades the user to a new plan via Stripe.

**Request:**
```json
{
  "plan": "business",
  "payment_method_id": "pm_stripe_id_here"
}
```

**Response:**
```json
{
  "message": "Plan upgraded to Business successfully.",
  "plan": "business"
}
```

---

### `POST /billing/cancel`

Cancels the current subscription. Access continues until the end of the billing period.

**Response:**
```json
{
  "message": "Subscription cancelled. Access continues until 2026-04-27."
}
```

---

### `GET /billing/history`

Returns the user's payment history.

**Response:**
```json
{
  "payments": [
    {
      "amount": 1000,
      "currency": "jpy",
      "status": "succeeded",
      "date": "2026-03-01T00:00:00Z"
    }
  ]
}
```

---

### `POST /billing/webhook`

Stripe webhook endpoint. Handles payment events from Stripe.

**Events handled:**
- `invoice.payment_succeeded` — activates or renews subscription
- `invoice.payment_failed` — sends payment failed notification to user
- `customer.subscription.deleted` — downgrades user to free plan

**Response:**
```json
{
  "received": true
}
```

---

## MCP Endpoints

### `GET /mcp/bucket/{mcp_token}`

Entry point for bucket-level MCP connections. Returns available tools and their schemas to the connecting AI.

**Response:**
```json
{
  "tools": [
    { "name": "search", "description": "Semantic search across all documents in the bucket." },
    { "name": "query", "description": "Ask a question and get a full AI-generated answer." },
    { "name": "list_files", "description": "List all files in the bucket." },
    { "name": "get_file", "description": "Get details of a specific file." },
    { "name": "get_file_summary", "description": "Get the AI-generated summary for a specific file." },
    { "name": "list_categories", "description": "List all categories in the bucket." },
    { "name": "get_bucket_info", "description": "Get bucket name, description, and storage info." },
    { "name": "get_file_layout", "description": "Get the full Layout JSON Map for a specific file." },
    { "name": "get_chunk", "description": "Get a specific chunk with its image metadata." },
    { "name": "list_chunks", "description": "List all chunks for a specific file." }
  ]
}
```

---

### `GET /mcp/account/{account_mcp_token}`

Entry point for account-level MCP connections. Returns available tools and their schemas to the connecting AI.

**Response:**
```json
{
  "tools": [
    { "name": "list_buckets", "description": "List all buckets in the account." },
    { "name": "create_bucket", "description": "Create a new bucket." },
    { "name": "get_bucket", "description": "Get full details of a specific bucket." },
    { "name": "delete_bucket", "description": "Delete a bucket and all its data." },
    { "name": "get_account_info", "description": "Get account info and usage stats." }
  ]
}
```

---

## Summary Table

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new account |
| POST | `/auth/verify-email` | Verify email address |
| POST | `/auth/login` | Login with email and password |
| POST | `/auth/2fa/verify` | Verify TOTP code during login |
| POST | `/auth/2fa/enable` | Enable 2FA |
| POST | `/auth/2fa/confirm` | Confirm 2FA setup |
| POST | `/auth/2fa/disable` | Disable 2FA |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout and blacklist token |
| POST | `/auth/forgot-password` | Send password reset email |
| POST | `/auth/reset-password` | Reset password with token |
| POST | `/auth/google` | Google OAuth login |
| POST | `/auth/github` | GitHub OAuth login |
| GET | `/user/profile` | Get current user profile |
| PUT | `/user/profile` | Update profile |
| PUT | `/user/avatar` | Upload profile picture |
| PUT | `/user/password` | Change password |
| DELETE | `/user/account` | Delete account |
| GET | `/buckets` | List all buckets |
| POST | `/buckets` | Create new bucket |
| GET | `/buckets/{id}` | Get bucket details |
| PUT | `/buckets/{id}` | Update bucket |
| DELETE | `/buckets/{id}` | Delete bucket |
| GET | `/buckets/{id}/mcp-url` | Get MCP URL |
| POST | `/buckets/{id}/mcp-url/regenerate` | Regenerate MCP token |
| POST | `/buckets/{id}/mcp-url/revoke` | Revoke MCP access |
| POST | `/buckets/{id}/files` | Upload files |
| GET | `/buckets/{id}/files` | List files |
| GET | `/buckets/{id}/files/{file_id}` | Get file details |
| DELETE | `/buckets/{id}/files/{file_id}` | Delete file |
| GET | `/buckets/{id}/files/{file_id}/summary` | Get file summary |
| GET | `/buckets/{id}/files/{file_id}/layout` | Get file layout JSON |
| GET | `/buckets/{id}/files/{file_id}/chunks` | List file chunks |
| GET | `/buckets/{id}/categories` | List categories |
| POST | `/buckets/{id}/categories` | Create category |
| DELETE | `/buckets/{id}/categories/{cat_id}` | Delete category |
| POST | `/buckets/{id}/search` | Semantic search |
| POST | `/buckets/{id}/query` | AI query with answer |
| GET | `/buckets/{id}/conversations` | List conversations |
| POST | `/buckets/{id}/conversations` | Create conversation |
| DELETE | `/buckets/{id}/conversations/{conv_id}` | Delete conversation |
| GET | `/buckets/{id}/conversations/{conv_id}/messages` | Get messages |
| POST | `/buckets/{id}/conversations/{conv_id}/messages` | Send message |
| GET | `/notifications` | Get notifications |
| PUT | `/notifications/read-all` | Mark all as read |
| DELETE | `/notifications/{id}` | Delete notification |
| GET | `/billing/plan` | Get current plan |
| POST | `/billing/upgrade` | Upgrade plan |
| POST | `/billing/cancel` | Cancel subscription |
| GET | `/billing/history` | Get payment history |
| POST | `/billing/webhook` | Stripe webhook |
| GET | `/mcp/bucket/{token}` | Bucket MCP entry point |
| GET | `/mcp/account/{token}` | Account MCP entry point |

---

*Document version: 1.0 — March 2026*
