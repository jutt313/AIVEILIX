# AIveilix Project Walkthrough

**Last Updated:** January 23, 2026  
**Project Type:** Full-Stack AI-Powered Knowledge Management Platform  
**Tech Stack:** FastAPI (Backend) + React (Frontend) + Supabase (Database) + DeepSeek AI

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Backend Deep Dive](#backend-deep-dive)
5. [Frontend Deep Dive](#frontend-deep-dive)
6. [Database Schema](#database-schema)
7. [Key Features](#key-features)
8. [API Endpoints](#api-endpoints)
9. [Environment Configuration](#environment-configuration)
10. [Setup & Running](#setup--running)

---

## 🎯 Project Overview

**AIveilix** is an intelligent knowledge management platform that allows users to:
- Create **buckets** (knowledge vaults) to organize documents
- Upload and process files (PDF, DOCX, TXT)
- Chat with their documents using AI (DeepSeek/Gemini)
- Access their knowledge via **MCP (Model Context Protocol)** for CLI/API integration
- Perform semantic search and full-text search across documents
- Manage API keys for programmatic access

### Core Capabilities
- 🤖 **AI-Powered Chat**: Chat with your documents using DeepSeek AI
- 🔍 **Semantic Search**: Vector-based similarity search using pgvector
- 📄 **Document Processing**: Extract and chunk text from various file formats
- 🔐 **Secure Authentication**: Supabase Auth with JWT tokens
- 🔑 **API Key Management**: Generate API keys for MCP/CLI access
- 📊 **Dashboard Analytics**: Track usage statistics and activity

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  - Vite + React 18 + TailwindCSS                            │
│  - Routes: Login, Signup, Dashboard, Bucket View            │
│  - Components: Chat, File Upload, API Key Management        │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  - Python 3.14 + FastAPI + Uvicorn                          │
│  - Routers: auth, buckets, files, chat, api_keys, mcp       │
│  - Services: Supabase, OAuth2, File Processing, Rate Limit  │
└────────────────────┬────────────────────────────────────────┘
                     │ PostgreSQL + pgvector
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database (Supabase)                        │
│  - PostgreSQL with pgvector extension                        │
│  - Tables: profiles, buckets, files, chunks, conversations  │
│  - Storage: File uploads in Supabase Storage                │
│  - Auth: Supabase Auth (JWT-based)                          │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI Services                             │
│  - DeepSeek API (Primary for chat)                          │
│  - Google Gemini API (Fallback/embeddings)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
AIveilix/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # Settings & environment config
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── models/            # Pydantic models (8 files)
│   │   │   ├── auth.py
│   │   │   ├── buckets.py
│   │   │   ├── files.py
│   │   │   ├── chat.py
│   │   │   ├── api_keys.py
│   │   │   └── mcp.py
│   │   ├── routers/           # API route handlers (7 files)
│   │   │   ├── auth.py        # Signup, login, password reset
│   │   │   ├── buckets.py     # CRUD for buckets
│   │   │   ├── files.py       # File upload & management
│   │   │   ├── chat.py        # AI chat with documents
│   │   │   ├── api_keys.py    # API key generation
│   │   │   ├── mcp.py         # MCP protocol endpoints
│   │   │   └── oauth.py       # OAuth2 flows
│   │   └── services/          # Business logic (6 files)
│   │       ├── supabase.py    # Supabase client
│   │       ├── oauth2.py      # JWT token handling
│   │       ├── file_processor.py  # File parsing & chunking
│   │       ├── mcp_auth.py    # MCP authentication
│   │       └── rate_limiter.py
│   ├── requirements.txt       # Python dependencies
│   ├── run.py                 # Server entry point
│   └── venv/                  # Python virtual environment
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.jsx            # Main app with routing
│   │   ├── main.jsx           # React entry point
│   │   ├── config.js          # API URL configuration
│   │   ├── index.css          # Global styles
│   │   ├── pages/             # Page components (5 files)
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   ├── ForgotPassword.jsx
│   │   │   ├── Dashboard.jsx  # Main dashboard with buckets
│   │   │   └── Bucket.jsx     # Individual bucket view
│   │   ├── components/        # Reusable components (17 files)
│   │   │   ├── AuthLayout.jsx
│   │   │   ├── BucketsTable.jsx
│   │   │   ├── ChatPanel.jsx  # AI chat interface
│   │   │   ├── FileUpload.jsx
│   │   │   ├── FilesCard.jsx
│   │   │   ├── ProfileModal.jsx
│   │   │   ├── CreateBucketModal.jsx
│   │   │   ├── CreateAPIKeyModal.jsx
│   │   │   └── ...
│   │   ├── context/           # React contexts
│   │   │   ├── AuthContext.jsx  # Auth state management
│   │   │   └── ThemeContext.jsx
│   │   └── services/
│   │       └── api.js         # Axios API client
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── supabase/                  # Database schema & migrations
│   ├── schema.sql             # Full database schema (552 lines)
│   ├── SETUP.md               # Supabase setup guide
│   └── migrations/
│
├── .env                       # Environment variables (ACTIVE)
├── env.template               # Environment template
└── PROJECT_WALKTHROUGH.md     # This file
```

---

## 🔧 Backend Deep Dive

### Core Files

#### `backend/run.py`
Entry point for the backend server. Runs Uvicorn with hot reload in development.

```python
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.backend_port,  # Default: 7223
        reload=settings.app_env == "development",
    )
```

#### `backend/app/config.py`
Centralized configuration using Pydantic Settings. Loads from `.env` file.

**Key Settings:**
- `supabase_url`, `supabase_anon_key`, `supabase_service_role_key`
- `database_url` (PostgreSQL connection string)
- `gemini_api_key`, `deepseek_api_key`
- `backend_port` (7223), `frontend_url` (http://localhost:6677)
- `mcp_rate_limit_per_hour` (100 requests)

#### `backend/app/main.py`
FastAPI application setup with:
- **CORS middleware** for frontend communication
- **Global exception handlers** for errors
- **Router registration** for all API endpoints

**Registered Routers:**
```python
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(buckets.router, prefix="/api/buckets", tags=["buckets"])
app.include_router(files.router, prefix="/api/buckets", tags=["files"])
app.include_router(chat.router, prefix="/api/buckets", tags=["chat"])
app.include_router(api_keys.router, prefix="/api/api-keys", tags=["api-keys"])
app.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
```

### Routers (API Endpoints)

#### 1. **`routers/auth.py`** - Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/forgot-password` - Send password reset email
- `POST /api/auth/reset-password` - Reset password with token
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change password (requires current password)
- `POST /api/auth/delete-account` - Delete user account

#### 2. **`routers/buckets.py`** - Bucket Management
- `GET /api/buckets` - List all user's buckets
- `POST /api/buckets` - Create new bucket
- `GET /api/buckets/{id}` - Get specific bucket
- `DELETE /api/buckets/{id}` - Delete bucket
- `POST /api/buckets/delete-all` - Delete all buckets (requires password)
- `GET /api/buckets/dashboard/stats` - Get dashboard statistics

#### 3. **`routers/files.py`** - File Management
- `POST /api/buckets/{bucket_id}/files` - Upload file to bucket
- `GET /api/buckets/{bucket_id}/files` - List files in bucket
- `GET /api/buckets/{bucket_id}/files/{file_id}` - Get file details
- `DELETE /api/buckets/{bucket_id}/files/{file_id}` - Delete file
- `GET /api/buckets/{bucket_id}/files/{file_id}/download` - Download file

#### 4. **`routers/chat.py`** - AI Chat
- `POST /api/buckets/{bucket_id}/chat` - Chat with bucket using DeepSeek AI
- Supports multiple modes: `full_scan`, `semantic_search`, `keyword_search`
- Streams responses using Server-Sent Events (SSE)

#### 5. **`routers/api_keys.py`** - API Key Management
- `GET /api/api-keys` - List user's API keys
- `POST /api/api-keys` - Create new API key
- `DELETE /api/api-keys/{key_id}` - Revoke API key

#### 6. **`routers/mcp.py`** - MCP Protocol (CLI/API Access)
- `GET /mcp/buckets` - List buckets (API key auth)
- `GET /mcp/buckets/{bucket_id}/files` - List files (API key auth)
- `POST /mcp/buckets/{bucket_id}/query` - Query bucket content
- `POST /mcp/buckets/{bucket_id}/chat` - Chat with bucket (API key auth)

### Services

#### `services/supabase.py`
Provides Supabase client instances:
- `get_supabase()` - Service role client (admin access)
- `get_supabase_auth()` - Anon client (user auth)

#### `services/oauth2.py`
JWT token handling:
- `create_access_token()` - Generate JWT tokens
- `verify_token()` - Validate JWT tokens
- `get_current_user()` - Extract user from token

#### `services/file_processor.py`
File parsing and chunking:
- Supports: PDF, DOCX, TXT
- Extracts text content
- Splits into chunks for embedding
- Calculates content hashes

#### `services/mcp_auth.py`
MCP authentication:
- Validates API keys
- Checks permissions and scopes
- Rate limiting integration

#### `services/rate_limiter.py`
Rate limiting for MCP endpoints:
- Tracks request counts per API key
- Configurable limits (default: 100/hour)

### Dependencies (`requirements.txt`)

**Core Framework:**
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server

**Database:**
- `supabase` - Supabase client
- `asyncpg` - PostgreSQL async driver
- `sqlalchemy` - ORM

**Auth & Security:**
- `python-jose[cryptography]` - JWT tokens
- `passlib[bcrypt]` - Password hashing
- `python-multipart` - File uploads

**AI/LLM:**
- `google-generativeai` - Gemini API
- `openai` - OpenAI-compatible API (for DeepSeek)

**File Processing:**
- `python-docx` - DOCX parsing
- `PyPDF2` - PDF parsing
- `python-magic` - File type detection

**Utils:**
- `pydantic[email]` - Data validation
- `pydantic-settings` - Settings management
- `python-dotenv` - Environment variables
- `httpx` - HTTP client
- `tenacity` - Retry logic
- `slowapi` - Rate limiting
- `mcp` - MCP protocol
- `authlib` - OAuth2

---

## 🎨 Frontend Deep Dive

### Tech Stack
- **React 18** - UI framework
- **Vite** - Build tool & dev server
- **TailwindCSS 4** - Styling
- **React Router v6** - Routing
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Supabase JS** - Supabase client

### Key Files

#### `src/App.jsx`
Main application with routing:
- Wraps app in `ThemeProvider` and `AuthProvider`
- Defines routes for login, signup, dashboard, bucket view
- Uses `ProtectedRoute` for authenticated pages

#### `src/main.jsx`
React entry point - renders `App` into `#root`

#### `src/config.js`
Configuration for API endpoints:
```javascript
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:7223',
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL || '',
  supabaseAnonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || '',
}
```

### Pages

#### 1. **`pages/Login.jsx`**
- Email/password login form
- Links to signup and forgot password
- Redirects to dashboard on success

#### 2. **`pages/Signup.jsx`**
- User registration form
- Email, password, full name fields
- Email verification flow

#### 3. **`pages/ForgotPassword.jsx`**
- Password reset request form
- Sends reset email via Supabase

#### 4. **`pages/Dashboard.jsx`**
- Main dashboard view
- Shows user's buckets in a table
- Dashboard statistics (buckets count, files count, total size)
- Create bucket modal
- Profile modal with settings
- API key management

#### 5. **`pages/Bucket.jsx`**
- Individual bucket view
- File list with upload capability
- Chat panel for AI interaction
- File management (delete, download)

### Key Components

#### **`components/ChatPanel.jsx`**
AI chat interface:
- Message history display
- Input field for user queries
- Streaming response handling
- Mode selection (full scan, semantic search, keyword search)
- Source citations display

#### **`components/FileUpload.jsx`**
Drag-and-drop file upload:
- Supports PDF, DOCX, TXT
- Progress indicator
- Multiple file upload

#### **`components/BucketsTable.jsx`**
Displays user's buckets in a table:
- Bucket name, description, file count, size
- Click to open bucket view
- Delete bucket action

#### **`components/CreateBucketModal.jsx`**
Modal for creating new buckets:
- Name and description fields
- Privacy toggle (private/public)

#### **`components/CreateAPIKeyModal.jsx`**
Modal for generating API keys:
- Key name input
- Scope selection (read, write)
- Bucket access restrictions
- Displays generated key (one-time view)

#### **`components/ProfileModal.jsx`**
User profile management:
- Display user info
- Change password
- Delete account (with confirmation)
- Danger zone for destructive actions

### Context Providers

#### **`context/AuthContext.jsx`**
Authentication state management:
- `user` - Current user object
- `loading` - Auth loading state
- `signup()` - Register new user
- `login()` - Authenticate user
- `logout()` - Sign out user
- `forgotPassword()` - Request password reset
- `isAuthenticated` - Boolean flag

Stores tokens in `localStorage`:
- `access_token`
- `refresh_token`
- `user` (JSON)

#### **`context/ThemeContext.jsx`**
Theme management (dark mode support)

### Services

#### **`services/api.js`**
Axios-based API client with:
- Base URL configuration
- Request interceptors (add auth token)
- Response interceptors (handle errors)
- Organized API methods:
  - `authAPI` - Auth endpoints
  - `bucketsAPI` - Bucket endpoints
  - `filesAPI` - File endpoints
  - `chatAPI` - Chat endpoints
  - `apiKeysAPI` - API key endpoints

---

## 🗄️ Database Schema

### Tables Overview

The database uses **PostgreSQL with pgvector extension** for semantic search.

#### 1. **`profiles`** - User profiles
- `id` (UUID, FK to auth.users)
- `email`, `full_name`, `avatar_url`
- `created_at`, `updated_at`

#### 2. **`buckets`** - Knowledge vaults
- `id` (UUID)
- `user_id` (UUID, FK to auth.users)
- `name`, `description`
- `is_private` (boolean)
- `file_count`, `total_size_bytes`
- `created_at`, `updated_at`

#### 3. **`categories`** - User-defined organization
- `id` (UUID)
- `user_id`, `bucket_id`
- `name`, `color`
- `parent_id` (self-referencing for hierarchy)

#### 4. **`files`** - Uploaded documents
- `id` (UUID)
- `user_id`, `bucket_id`, `category_id`
- `name`, `original_name`, `mime_type`, `size_bytes`
- `storage_path` (Supabase Storage path)
- `status` (pending, processing, ready, failed)
- `page_count`, `word_count`, `language`
- `processed_at`, `created_at`, `updated_at`

#### 5. **`chunks`** - Extracted text pieces
- `id` (UUID)
- `user_id`, `bucket_id`, `file_id`
- `content`, `content_hash`
- `chunk_index`, `page_number`, `start_offset`, `end_offset`
- `embedding` (vector(768)) - **pgvector for semantic search**
- `token_count`
- `content_tsv` (tsvector) - **Full-text search**

**Indexes:**
- IVFFlat index on `embedding` for fast vector similarity
- GIN index on `content_tsv` for full-text search

#### 6. **`summaries`** - AI-generated summaries
- `id` (UUID)
- `user_id`, `bucket_id`, `file_id`
- `summary_type` (file, bucket, section)
- `title`, `content`
- `key_facts`, `entities` (JSONB)
- `model_used`

#### 7. **`api_keys`** - MCP access tokens
- `id` (UUID)
- `user_id`
- `name`, `key_hash`, `key_prefix`
- `scopes` (array of strings: read, write)
- `allowed_buckets` (array of UUIDs)
- `last_used_at`, `request_count`
- `is_active`, `expires_at`, `revoked_at`

#### 8. **`conversations`** - Chat sessions
- `id` (UUID)
- `user_id`, `bucket_id`
- `title`, `mode` (full_scan, semantic_search, keyword_search)
- `created_at`, `updated_at`

#### 9. **`messages`** - Chat messages
- `id` (UUID)
- `user_id`, `conversation_id`
- `role` (user, assistant, system)
- `content`
- `model_used`, `tokens_used`
- `sources` (JSONB) - Citations

#### 10. **`actions`** - AI-proposed changes
- `id` (UUID)
- `user_id`, `conversation_id`, `message_id`
- `action_type` (categorize, edit_doc, delete, merge, split, tag)
- `status` (pending, approved, rejected, executed, failed)
- `description`, `target_type`, `target_id`
- `before_state`, `after_state` (JSONB)

### Key Functions

#### Search Functions

**`search_chunks(user_id, bucket_id, query, limit)`**
- Full-text search using PostgreSQL's `tsvector`
- Returns ranked results

**`search_chunks_semantic(user_id, bucket_id, embedding, limit)`**
- Vector similarity search using pgvector
- Returns chunks ordered by cosine similarity

**`full_scan_chunks(user_id, bucket_id)`**
- Returns ALL chunks from a bucket
- Used for comprehensive AI analysis

### Row-Level Security (RLS)

All tables have RLS enabled with policies:
- Users can only access their own data
- Enforced at database level (not just application)

### Triggers

- **Auto-update timestamps** on all tables with `updated_at`
- **Auto-create profile** when new user signs up
- **Update bucket stats** when files are added/removed

---

## ✨ Key Features

### 1. **Bucket Management**
- Create unlimited buckets (knowledge vaults)
- Organize files by bucket
- Track file count and total size per bucket
- Delete individual or all buckets

### 2. **File Processing**
- Upload PDF, DOCX, TXT files
- Automatic text extraction
- Chunking for efficient search
- Content deduplication via hashing
- Background processing pipeline

### 3. **AI Chat**
Three search modes:
- **Full Scan**: Analyzes entire bucket content
- **Semantic Search**: Vector similarity using embeddings
- **Keyword Search**: Traditional full-text search

Uses **DeepSeek AI** for chat responses with streaming support.

### 4. **MCP Protocol Support**
Allows CLI/API access via API keys:
- Generate API keys with custom scopes
- Restrict access to specific buckets
- Rate limiting (100 requests/hour default)
- Track usage statistics

### 5. **Authentication & Security**
- Supabase Auth (email/password)
- JWT token-based authentication
- Password reset via email
- Account deletion with verification
- Row-level security in database

### 6. **Dashboard Analytics**
- Total buckets count
- Total files count
- Total storage used
- Recent activity tracking

---

## 🔌 API Endpoints

### Authentication (`/api/auth`)
```
POST   /api/auth/signup              - Create account
POST   /api/auth/login               - Login
POST   /api/auth/logout              - Logout
GET    /api/auth/me                  - Get current user
POST   /api/auth/forgot-password     - Request password reset
POST   /api/auth/reset-password      - Reset password
POST   /api/auth/change-password     - Change password
POST   /api/auth/delete-account      - Delete account
```

### Buckets (`/api/buckets`)
```
GET    /api/buckets                  - List buckets
POST   /api/buckets                  - Create bucket
GET    /api/buckets/{id}             - Get bucket
DELETE /api/buckets/{id}             - Delete bucket
POST   /api/buckets/delete-all       - Delete all buckets
GET    /api/buckets/dashboard/stats  - Dashboard stats
```

### Files (`/api/buckets/{bucket_id}/files`)
```
GET    /api/buckets/{bucket_id}/files              - List files
POST   /api/buckets/{bucket_id}/files              - Upload file
GET    /api/buckets/{bucket_id}/files/{file_id}    - Get file
DELETE /api/buckets/{bucket_id}/files/{file_id}    - Delete file
GET    /api/buckets/{bucket_id}/files/{file_id}/download - Download
```

### Chat (`/api/buckets/{bucket_id}/chat`)
```
POST   /api/buckets/{bucket_id}/chat  - Chat with bucket (SSE stream)
```

### API Keys (`/api/api-keys`)
```
GET    /api/api-keys           - List API keys
POST   /api/api-keys           - Create API key
DELETE /api/api-keys/{key_id}  - Revoke API key
```

### MCP Protocol (`/mcp`)
```
GET    /mcp/buckets                         - List buckets (API key)
GET    /mcp/buckets/{bucket_id}/files       - List files (API key)
POST   /mcp/buckets/{bucket_id}/query       - Query bucket (API key)
POST   /mcp/buckets/{bucket_id}/chat        - Chat (API key)
```

---

## ⚙️ Environment Configuration

### `.env` File (Current Active Configuration)

```env
# Supabase Configuration
SUPABASE_URL=https://eaeerftdgpkaitxtpluu.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database (Direct PostgreSQL connection)
DATABASE_URL=postgresql://postgres:REDACTED_DB_PASSWORD@db.eaeerftdgpkaitxtpluu.supabase.co:5432/postgres

# Gemini API
GEMINI_API_KEY=REDACTED_GEMINI_KEY

# DeepSeek API (Primary AI for chat)
DEEPSEEK_API_KEY=REDACTED_DEEPSEEK_KEY

# App Configuration
APP_ENV=development
APP_SECRET_KEY=generate_a_random_secret_key_here
```

### `env.template` File (Template for New Setups)

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
GEMINI_API_KEY=your_gemini_api_key
APP_ENV=development
APP_SECRET_KEY=generate_a_random_secret_key_here
```

### Backend Configuration (`backend/app/config.py`)

**Default Values:**
- `backend_port`: 7223
- `frontend_url`: http://localhost:6677
- `mcp_rate_limit_per_hour`: 100
- `mcp_rate_limit_window`: 3600 seconds
- `oauth_redirect_uri`: http://localhost:7223/oauth/callback

### Frontend Configuration (`frontend/src/config.js`)

**Environment Variables (Vite):**
- `VITE_API_URL` - Backend API URL (default: http://localhost:7223)
- `VITE_SUPABASE_URL` - Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Supabase anon key

---

## 🚀 Setup & Running

### Prerequisites
- Python 3.14+
- Node.js 18+
- Supabase account
- DeepSeek API key
- Gemini API key (optional)

### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
- Copy `env.template` to `.env` in project root
- Fill in Supabase credentials
- Add DeepSeek API key
- Add Gemini API key (optional)

4. **Run backend:**
```bash
python run.py
```
Server runs on: http://localhost:7223

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Run frontend:**
```bash
npm run dev
```
Frontend runs on: http://localhost:6677

### Database Setup

1. **Create Supabase project** (see `supabase/SETUP.md`)
2. **Enable pgvector extension**
3. **Run schema:**
   - Open Supabase SQL Editor
   - Copy contents of `supabase/schema.sql`
   - Execute
4. **Create storage bucket** named `files` (private)
5. **Add storage RLS policies** (see `supabase/SETUP.md`)

### Verification

1. **Check backend health:**
```bash
curl http://localhost:7223/health
```

2. **Check frontend:**
Open http://localhost:6677 in browser

3. **Create test account:**
- Go to signup page
- Create account with email/password
- Verify email (check Supabase Auth dashboard)

---

## 📊 Data Flow Examples

### File Upload Flow
```
1. User uploads file via FileUpload.jsx
2. Frontend sends multipart/form-data to POST /api/buckets/{id}/files
3. Backend (files.py):
   - Validates file type and size
   - Uploads to Supabase Storage
   - Creates file record in database (status: pending)
4. Background processing (file_processor.py):
   - Extracts text from file
   - Splits into chunks
   - Generates embeddings (optional)
   - Stores chunks in database
   - Updates file status to 'ready'
5. Frontend polls for file status
6. User can now chat with the file
```

### Chat Flow
```
1. User types message in ChatPanel.jsx
2. Frontend sends POST /api/buckets/{id}/chat with:
   - message: "What is this document about?"
   - mode: "full_scan"
3. Backend (chat.py):
   - Retrieves chunks based on mode:
     * full_scan: All chunks
     * semantic_search: Vector similarity
     * keyword_search: Full-text search
   - Constructs prompt with chunks as context
   - Streams response from DeepSeek API
4. Frontend receives SSE stream
5. ChatPanel displays streaming response
6. Response saved to messages table
```

### MCP API Key Flow
```
1. User creates API key in CreateAPIKeyModal.jsx
2. Frontend sends POST /api/api-keys with:
   - name: "My CLI Key"
   - scopes: ["read", "write"]
   - allowed_buckets: [bucket_id]
3. Backend (api_keys.py):
   - Generates random API key (32 chars)
   - Hashes key with bcrypt
   - Stores hash and prefix in database
   - Returns full key (one-time view)
4. User copies key and uses in CLI:
   ```bash
   curl -H "Authorization: Bearer aiv_..." \
        http://localhost:7223/mcp/buckets
   ```
5. Backend (mcp.py):
   - Validates API key hash
   - Checks scopes and bucket access
   - Rate limits request
   - Returns data
```

---

## 🔍 Notable Implementation Details

### 1. **Streaming Chat Responses**
Uses Server-Sent Events (SSE) for real-time streaming:
```python
async def chat_endpoint():
    async def event_stream():
        for chunk in ai_response:
            yield f"data: {json.dumps(chunk)}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### 2. **API Key Security**
- Keys are hashed with bcrypt before storage
- Only prefix (first 8 chars) stored in plaintext for identification
- Full key shown only once at creation
- Keys can be scoped to specific buckets and permissions

### 3. **File Processing Pipeline**
- Asynchronous processing to avoid blocking uploads
- Content hashing to detect duplicates
- Chunking strategy: 500-word chunks with 50-word overlap
- Supports multiple file formats with fallback handling

### 4. **Vector Search Optimization**
- Uses IVFFlat index for fast approximate nearest neighbor search
- Embedding dimension: 768 (compatible with many models)
- Cosine similarity metric for relevance scoring

### 5. **Row-Level Security**
All database queries automatically filtered by user_id:
```sql
CREATE POLICY "Users can view own buckets" ON public.buckets
    FOR SELECT USING (auth.uid() = user_id);
```

### 6. **Rate Limiting**
MCP endpoints use sliding window rate limiting:
- Tracks requests per API key
- Configurable limits (default: 100/hour)
- Returns 429 Too Many Requests when exceeded

---

## 🎯 Next Steps & Potential Enhancements

### Planned Features (Based on Conversation History)
1. **Enhanced Dashboard Stats** - More detailed analytics
2. **Project Management** - Track AI agent projects
3. **Live Agent** - Silent monitoring and error fixing
4. **Consolidated Agent Architecture** - MainAgent, CodeAgent, LiveAgent
5. **Profile Enhancements** - More user customization options

### Potential Improvements
1. **Batch File Upload** - Upload multiple files at once
2. **File Versioning** - Track document changes over time
3. **Collaborative Buckets** - Share buckets with other users
4. **Advanced Search Filters** - Filter by date, file type, category
5. **Export Functionality** - Export chat history, summaries
6. **Webhook Support** - Notify external systems of events
7. **Custom Embeddings** - Support for different embedding models
8. **OCR Support** - Extract text from images in PDFs
9. **Audio/Video Transcription** - Process multimedia files
10. **Multi-language Support** - Internationalization

---

## 📝 Notes

- **DeepSeek API** is the primary AI provider for chat functionality
- **Gemini API** can be used as a fallback or for embeddings
- The project uses **Supabase** for both database and authentication
- **MCP Protocol** enables CLI/API integration for power users
- All file uploads are stored in **Supabase Storage** with RLS policies
- The frontend uses **TailwindCSS 4** for modern, responsive design
- **React Router v6** handles client-side routing
- **Vite** provides fast development builds and HMR

---

## 🔗 Useful Links

- **Supabase Dashboard**: https://supabase.com/dashboard
- **Google AI Studio** (Gemini): https://aistudio.google.com/app/apikey
- **DeepSeek API**: https://platform.deepseek.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **TailwindCSS Docs**: https://tailwindcss.com/

---

**End of Walkthrough**

*This document provides a comprehensive overview of the AIveilix project structure, architecture, and implementation details. For specific implementation questions, refer to the source code or the conversation history.*
