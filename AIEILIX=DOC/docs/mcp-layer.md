# Aiveilix — MCP Layer

> This document describes the complete MCP (Model Context Protocol) layer for Aiveilix. It covers the two MCP URL types, all exposed tools, authentication flow, and how external AI tools connect to user buckets.

---

## Overview

Every Aiveilix user gets two types of MCP URLs. These URLs allow any MCP-compatible AI — including Claude, ChatGPT, and custom agents — to connect directly to a user's knowledge bucket and interact with it in real time.

| MCP URL Type | Scope | Purpose |
|---|---|---|
| **Bucket MCP URL** | Single bucket | Access, search, and query one specific bucket |
| **Account MCP URL** | All buckets | Manage all buckets from one endpoint |

The auth token is baked directly into the URL. The user pastes the URL into any AI tool and it connects immediately — no extra login or setup required.

---

## MCP URL Structure

### Bucket MCP URL

```
https://mcp.aiveilix.com/bucket/{mcp_token}
```

Each bucket has its own unique token. The token lives forever unless the user revokes it manually.

**Example:**
```
https://mcp.aiveilix.com/bucket/tok_abc123xyz789
```

---

### Account MCP URL

```
https://mcp.aiveilix.com/account/{account_mcp_token}
```

One URL per user account. Gives access to all buckets and account-level management tools.

**Example:**
```
https://mcp.aiveilix.com/account/acc_tok_xyz789abc
```

---

## Authentication Flow

Every request to an MCP URL is authenticated by verifying the token against the `api_keys` table in PostgreSQL.

```
External AI sends request to MCP URL
        |
        v
FastAPI extracts token from URL path
        |
        v
Look up token in PostgreSQL api_keys table
        |
        v
Check is_active = true
        |
        v
Fetch associated bucket_id or user_id
        |
        v
Update last_used_at timestamp
        |
        v
Allow access to requested tool
```

If the token is invalid or revoked, the request is rejected with a clean error message.

---

## Bucket MCP URL — Exposed Tools

These tools are available when an AI connects using a Bucket MCP URL. All tools operate on the specific bucket linked to the token.

---

### 1. `search`

Performs semantic search across all documents in the bucket. RAG, Layout JSON, and the BGE Reranker are all applied to retrieve the most relevant results.

**Input:**
```json
{
  "query": "What was the revenue in August?",
  "top_k": 5
}
```

**Output:**
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

### 2. `query`

Asks a natural language question. The system runs search, reranking, and Layout JSON context assembly, then sends everything to Claude to generate a full answer.

**Input:**
```json
{
  "question": "What was the revenue in August?"
}
```

**Output:**
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

### 3. `list_files`

Lists all files in the bucket with their metadata.

**Input:** none

**Output:**
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

### 4. `get_file`

Gets the full details of a specific file.

**Input:**
```json
{
  "file_id": "f_abc123"
}
```

**Output:**
```json
{
  "file_id": "f_abc123",
  "name": "company-report.pdf",
  "type": "pdf",
  "size": 2048000,
  "page_count": 10,
  "status": "ready",
  "created_at": "2026-03-15T08:00:00Z"
}
```

---

### 5. `get_file_summary`

Returns the AI-generated summary for a specific file. Each file has its own dedicated summary stored in the `summaries` table.

**Input:**
```json
{
  "file_id": "f_abc123"
}
```

**Output:**
```json
{
  "file_id": "f_abc123",
  "file_name": "company-report.pdf",
  "summary": "This report covers Q3 financial performance. Total revenue grew 23% driven by Asia-Pacific expansion. August was the strongest month at $230,000. The report includes charts, tables, and regional breakdowns."
}
```

---

### 6. `list_categories`

Lists all categories inside the bucket.

**Input:** none

**Output:**
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

### 7. `get_bucket_info`

Returns general information about the bucket.

**Input:** none

**Output:**
```json
{
  "bucket_id": "b_xyz789",
  "name": "Company Research",
  "description": "All company research documents",
  "storage_used": 52428800,
  "files_count": 12,
  "created_at": "2026-03-10T09:00:00Z"
}
```

---

### 8. `get_file_layout`

Returns the full Layout JSON Map for a specific file. This gives the AI the exact position of every text block, table, and image on every page.

**Input:**
```json
{
  "file_id": "f_abc123"
}
```

**Output:**
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

### 9. `get_chunk`

Returns a specific chunk with its full metadata including nearby image information.

**Input:**
```json
{
  "chunk_id": "chunk_001"
}
```

**Output:**
```json
{
  "chunk_id": "chunk_001",
  "file_id": "f_abc123",
  "file_name": "company-report.pdf",
  "page": 1,
  "content": "Total revenue increased by 23% this quarter.",
  "nearby_image": {
    "image_id": "img_1",
    "description": "A blue bar chart showing monthly revenue growth.",
    "text_inside": "July: $200k, August: $230k, September: $260k"
  }
}
```

---

### 10. `list_chunks`

Lists all chunks for a specific file. Useful for agents that want to navigate a file precisely.

**Input:**
```json
{
  "file_id": "f_abc123"
}
```

**Output:**
```json
{
  "chunks": [
    {
      "chunk_id": "chunk_001",
      "page": 1,
      "content": "Total revenue increased by 23% this quarter.",
      "token_count": 24
    },
    {
      "chunk_id": "chunk_002",
      "page": 1,
      "content": "Asia-Pacific region led growth with a 35% increase.",
      "token_count": 18
    }
  ]
}
```

---

## Account MCP URL — Exposed Tools

These tools are available when an AI connects using an Account MCP URL. They operate across all buckets belonging to the user.

---

### 1. `list_buckets`

Lists all buckets in the user account.

**Input:** none

**Output:**
```json
{
  "buckets": [
    {
      "bucket_id": "b_xyz789",
      "name": "Company Research",
      "files_count": 12,
      "storage_used": 52428800,
      "mcp_url": "https://mcp.aiveilix.com/bucket/tok_abc123xyz",
      "created_at": "2026-03-10T09:00:00Z"
    }
  ]
}
```

---

### 2. `create_bucket`

Creates a new bucket in the user account from an external service or agent.

**Input:**
```json
{
  "name": "Legal Documents",
  "description": "All legal contracts and agreements",
  "color": "#10B981"
}
```

**Output:**
```json
{
  "bucket_id": "b_new123",
  "name": "Legal Documents",
  "mcp_url": "https://mcp.aiveilix.com/bucket/tok_new123xyz",
  "created_at": "2026-03-27T10:00:00Z"
}
```

---

### 3. `get_bucket`

Gets full details of a specific bucket.

**Input:**
```json
{
  "bucket_id": "b_xyz789"
}
```

**Output:**
```json
{
  "bucket_id": "b_xyz789",
  "name": "Company Research",
  "description": "All company research documents",
  "storage_used": 52428800,
  "files_count": 12,
  "mcp_url": "https://mcp.aiveilix.com/bucket/tok_abc123xyz",
  "created_at": "2026-03-10T09:00:00Z"
}
```

---

### 4. `delete_bucket`

Deletes a bucket and all its files and embeddings.

**Input:**
```json
{
  "bucket_id": "b_xyz789"
}
```

**Output:**
```json
{
  "success": true,
  "message": "Bucket deleted successfully."
}
```

---

### 5. `get_account_info`

Returns overall account information and usage stats.

**Input:** none

**Output:**
```json
{
  "user_id": "u_abc123",
  "email": "user@example.com",
  "plan": "pro",
  "storage_used": 104857600,
  "storage_limit": 10737418240,
  "buckets_count": 5,
  "files_count": 48
}
```

---

## How External AI Connects

### Step 1 — User copies MCP URL

The user copies their bucket or account MCP URL from the Aiveilix dashboard.

```
https://mcp.aiveilix.com/bucket/tok_abc123xyz789
```

### Step 2 — User pastes into AI tool

The user pastes the URL into Claude, ChatGPT custom GPT actions, or any MCP-compatible agent.

### Step 3 — AI connects and discovers tools

The AI sends a request to the MCP URL and receives the list of available tools with their schemas.

### Step 4 — AI calls tools in real time

```
Agent asks: "What does the Q3 report say about August revenue?"
        |
        v
Agent calls: search({ query: "August revenue Q3 report" })
        |
        v
Aiveilix runs RAG, reranker, and Layout JSON
        |
        v
Returns top 5 relevant chunks with image context
        |
        v
Agent generates answer using retrieved context
```

---

## MCP Token Management

### Revoke Token

```
User clicks "Revoke MCP Access" in bucket settings
        |
        v
api_keys.is_active = false
        |
        v
Token is immediately invalid
All AI connections using this token are disconnected
        |
        v
User can generate a new token at any time
```

---

## Summary of All Tools

### Bucket MCP URL Tools

| Tool | Description |
|---|---|
| `search` | Semantic search with RAG, Layout JSON, and reranker applied |
| `query` | Ask a question and get a full AI-generated answer |
| `list_files` | List all files in the bucket |
| `get_file` | Get details of a specific file |
| `get_file_summary` | Get the AI-generated summary for a specific file |
| `list_categories` | List all categories in the bucket |
| `get_bucket_info` | Get bucket name, description, and storage info |
| `get_file_layout` | Get the full Layout JSON Map for a specific file |
| `get_chunk` | Get a specific chunk with its image metadata |
| `list_chunks` | List all chunks for a specific file |

### Account MCP URL Tools

| Tool | Description |
|---|---|
| `list_buckets` | List all buckets in the account |
| `create_bucket` | Create a new bucket |
| `get_bucket` | Get full details of a specific bucket |
| `delete_bucket` | Delete a bucket and all its data |
| `get_account_info` | Get account info and usage stats |

---

*Document version: 1.0 — March 2026*
