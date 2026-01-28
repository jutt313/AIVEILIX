# AIveilix - Comprehensive Project Knowledge Base

## What is AIveilix?
AI-powered Knowledge Management Platform - an intelligent document vault system where users can upload documents (including images, PDFs, code files), organize them in "buckets" (vaults), and interact with their documents using AI-powered chat with semantic search capabilities.

## Tech Stack
- **Backend**: FastAPI (Python 3.14) on port 7223
- **Frontend**: React 18 + Vite on port 6677
- **Database**: PostgreSQL + pgvector (via Supabase)
- **AI**: DeepSeek (chat), OpenAI (embeddings + vision), Google Gemini (fallback)
- **Styling**: TailwindCSS 4
- **Authentication**: Supabase Auth (JWT tokens)
- **Storage**: Supabase Storage (file uploads)

---

## Architecture Overview

```
User → Frontend (React) → REST API → FastAPI Backend → Services Layer
                                          ↓
                        PostgreSQL + pgvector (Supabase)
                                          ↓
                        AI APIs (DeepSeek, OpenAI, Gemini)
                        Google Custom Search API
```

---

## 1. BACKEND ARCHITECTURE

### 1.1 Core Entry Points

**`backend/run.py`**
- Uvicorn server launcher on port 7223
- Hot reload enabled in development

**`backend/app/main.py`**
- FastAPI app initialization
- Comprehensive logging (colored, timestamped)
- CORS middleware (frontend + ChatGPT/OAuth origins)
- Global exception handling with error tracking
- Request/response logging middleware
- 9 routers: auth, buckets, files, chat, api_keys, mcp, mcp_server, oauth, notifications

**`backend/app/config.py`**
- Pydantic Settings for environment management
- Key settings:
  - Supabase URL, anon key, service role key
  - Database URL (direct PostgreSQL connection)
  - DeepSeek API key (primary chat AI)
  - OpenAI API key (embeddings + GPT-4o Vision)
  - Google Search API (web search in chat)
  - MCP settings (rate limiting, transports)
  - OAuth2 settings (token expiry, secrets)

---

### 1.2 API Routers & Endpoints

#### Auth Router (`routers/auth.py`)
User authentication via Supabase Auth:
- `POST /api/auth/signup` - Create account with email verification
- `POST /api/auth/login` - Login (creates notification)
- `POST /api/auth/logout` - Sign out
- `GET /api/auth/me` - Get current user from JWT
- `POST /api/auth/forgot-password` - Send password reset email
- `POST /api/auth/reset-password` - Reset with token
- `POST /api/auth/change-password` - Change password (requires current password)
- `POST /api/auth/delete-account` - Delete account (requires password)

**Auth Flow:**
1. Signup → Supabase Auth creates user → Database trigger creates profile
2. Login → JWT access + refresh tokens returned
3. Frontend stores tokens in localStorage
4. All requests include `Authorization: Bearer <token>` header

#### Buckets Router (`routers/buckets.py`)
Knowledge vault management:
- `GET /api/buckets` - List user's buckets (ordered by created_at desc)
- `POST /api/buckets` - Create bucket (auto-generates UUID, creates notification)
- `GET /api/buckets/{id}` - Get bucket details
- `DELETE /api/buckets/{id}` - Delete bucket (cascade deletes files/chunks)
- `POST /api/buckets/delete-all` - Delete all (requires password)
- `GET /api/buckets/stats/dashboard` - Dashboard stats (total buckets, files, storage)
- `GET /api/buckets/stats/activity` - Activity data for date range (cumulative counts)

**Features:**
- Password verification for destructive operations
- Auto-update file_count and total_size_bytes via triggers
- Activity tracking with configurable date range

#### Files Router (`routers/files.py`)
File upload and processing:
- `POST /api/buckets/{bucket_id}/upload` - Upload file (multipart/form-data)
- `GET /api/buckets/{bucket_id}/files` - List files
- `GET /api/buckets/{bucket_id}/files/{file_id}/content` - Get file (summary + full text)
- `PUT /api/buckets/{bucket_id}/files/{file_id}/summary` - Update summary
- `GET /api/buckets/{bucket_id}/search` - Keyword search (files, chunks, summaries)
- `GET /api/buckets/{bucket_id}/semantic-search` - Vector/hybrid search
- `DELETE /api/buckets/{bucket_id}/files/{file_id}` - Delete file

**File Processing Pipeline:**
1. **Upload**: Save to temp → Upload to Supabase Storage → Create file record (status: processing)
2. **Text Extraction**:
   - **Images** (jpg, png, gif, etc.): GPT-4o Vision API for OCR + description
   - **PDFs**: PyMuPDF extracts text + embedded images (via Vision API)
   - **DOCX**: python-docx extracts paragraphs
   - **CSV**: Read and format rows
   - **Code/text**: 50+ extensions (py, js, ts, md, html, css, json, yml, etc.)
3. **Chunking**: 150-word chunks with 50-word overlap
4. **Embeddings**: Batch generation using OpenAI `text-embedding-3-large` (3072 dimensions)
5. **AI Summary**: Optional on-demand analysis via DeepSeek
6. **Status Update**: Mark as "ready" or "failed"

**Intelligent Fallback:**
- If chunks insufficient (<500 chars), fetches full file from storage
- Ensures comprehensive content for chat

**Search Modes:**
- **Keyword**: Full-text search using PostgreSQL tsvector
- **Semantic**: Vector similarity using pgvector cosine distance
- **Hybrid**: Combines both (recommended)

#### Chat Router (`routers/chat.py`)
AI-powered document chat:
- `POST /api/buckets/{bucket_id}/chat` - Chat with bucket (DeepSeek AI)
- `GET /api/buckets/{bucket_id}/conversations` - List conversations
- `GET /api/conversations/{conversation_id}/messages` - Get messages
- `PATCH /api/conversations/{conversation_id}` - Update title
- `DELETE /api/conversations/{conversation_id}` - Delete conversation

**Chat Flow:**
1. **Context Building**:
   - File inventory (ALL files, processed + unprocessed)
   - Comprehensive analyses (summaries)
   - Raw chunks (up to 1000 chars each)
   - Full file fallback if chunks < 500 chars
   - Web search results (auto-triggered for relevant queries)
2. **Conversation Management**:
   - Auto-create conversation on first message
   - Load previous messages (up to 10) for context
   - Save user + assistant messages to database
3. **AI Integration**:
   - DeepSeek `deepseek-chat` model
   - System prompt with strict formatting (no markdown)
   - Temperature 0.7 for balanced creativity
   - Source tracking (files, chunks, summaries, web)
4. **Web Search Integration**:
   - Auto-detection of queries needing external info
   - Google Custom Search API
   - Results formatted and cited

#### API Keys Router (`routers/api_keys.py`)
Generate API keys for MCP/CLI:
- `POST /api/api-keys` - Create key (returns full key ONCE)
- `GET /api/api-keys` - List keys (never returns full key)
- `DELETE /api/api-keys/{key_id}` - Revoke key

**Security:**
- Format: `aiveilix_sk_live_<32-byte-random-token>`
- SHA-256 hashing before storage
- Only prefix stored in plaintext (first 12 chars)
- Scopes: read, write, delete (granular permissions)
- Optional bucket restrictions (null = all, array = specific)
- Usage tracking: last_used_at, request_count
- Expiration support

#### MCP Router (`routers/mcp.py`)
MCP protocol for external access (Cursor, ChatGPT, CLI):
- `GET /mcp/buckets` - List accessible buckets
- `GET /mcp/buckets/{bucket_id}/files` - List files
- `POST /mcp/buckets/{bucket_id}/query` - Semantic search
- `POST /mcp/buckets/{bucket_id}/chat` - Chat with bucket

**Security:**
- API key authentication (hash validation, active status, expiration)
- Rate limiting (100 requests/hour per key)
- Bucket access verification (owner + allowed_buckets)
- Cross-user access prevention
- Error sanitization
- Usage tracking

**Same intelligent processing** as chat router (full file fallback, summaries, chunks)

#### MCP Server Router (`routers/mcp_server.py`)
Official MCP protocol server:
- Implements MCP SDK for ChatGPT/Cursor
- OAuth2 flow support
- Resources, tools, prompts endpoints

#### OAuth Router (`routers/oauth.py`)
OAuth2 client management:
- `POST /api/oauth/clients` - Create OAuth client
- `GET /api/oauth/clients` - List clients
- `DELETE /api/oauth/clients/{client_id}` - Revoke client
- `GET /api/oauth/authorize` - Authorization endpoint
- `POST /api/oauth/token` - Token exchange/refresh

#### Notifications Router (`routers/notifications.py`)
User notifications:
- `GET /api/notifications` - List notifications
- `PATCH /api/notifications/{notification_id}/read` - Mark as read
- `POST /api/notifications/read-all` - Mark all as read

---

### 1.3 Services Layer

#### Supabase Service (`services/supabase.py`)
- `supabase`: Service role client (admin access, bypasses RLS)
- `supabase_auth`: Anon key client (for auth operations)

#### OAuth2 Service (`services/oauth2.py`)
Comprehensive OAuth2 implementation:
- Client management (create, validate, list, revoke)
- Authorization codes (10-min expiry, one-time use)
- Token management (access 60 min, refresh 30 days)
- SHA-256 hashing for secrets/codes/tokens
- Scope mapping (API key scopes → MCP scopes)

#### File Processor Service (`services/file_processor.py`)
Advanced file processing:

**Supported Formats:**
- **Images**: JPG, PNG, GIF, BMP, WebP, TIFF → GPT-4o Vision
- **PDFs**: Text + embedded images (PyMuPDF + Vision)
- **Documents**: DOCX (python-docx)
- **Data**: CSV
- **Code**: 50+ types (py, js, ts, md, html, css, json, yml, etc.)

**Key Functions:**
- `extract_text_from_file()`: Multi-format extraction
- `process_image_with_vision()`: GPT-4o Vision OCR + description
- `chunk_text()`: 150-word chunks, 50-word overlap
- `generate_embedding()`: OpenAI text-embedding-3-large (3072-dim)
- `generate_embeddings_batch()`: Batch processing (faster)
- `analyze_file_comprehensive()`: DeepSeek analysis
- `fetch_full_file_content()`: Download + re-extract from storage

#### Semantic Search Service (`services/semantic_search.py`)
Vector similarity search:
- `semantic_search()`: pgvector cosine similarity via RPC
- `hybrid_search()`: Combines semantic + keyword (deduplication)
- `format_semantic_results_for_context()`: Format for AI

#### MCP Auth Service (`services/mcp_auth.py`)
Unified MCP authentication:
- OAuth2 tokens + API keys support
- `get_mcp_user()`: Main dependency for MCP endpoints
- `check_mcp_scope()`: Scope validation
- `check_bucket_access_mcp()`: Bucket permission check
- Scope mapping: read, write, query, chat, full

#### Rate Limiter Service (`services/rate_limiter.py`)
Sliding window rate limiting:
- Default: 100 requests/hour per API key
- In-memory tracking

#### Web Search Service (`services/web_search.py`)
Google Custom Search integration:
- `search_web()`: Query Google API
- `should_search_web()`: Auto-detect queries needing external info
- `format_search_results_for_context()`: Format for AI

#### Notifications Service (`services/notifications.py`)
Create user notifications:
- Types: login, file_upload, file_processed, bucket_created, api_key_created

---

### 1.4 Data Models (Pydantic)

Located in `backend/app/models/`:
- **auth.py**: SignupRequest, LoginRequest, AuthResponse
- **buckets.py**: BucketCreate, BucketResponse, DashboardStats
- **files.py**: FileResponse, ChatRequest, ChatResponse, SearchResult
- **api_keys.py**: CreateAPIKeyRequest, APIKeyResponse
- **mcp.py**: MCPBucketResponse, MCPQueryRequest, MCPChatResponse
- **oauth.py**: OAuthClientCreate, OAuthTokenResponse, MCPUser

---

### 1.5 MCP Stdio Entry Point

**`backend/app/mcp_stdio.py`**
- MCP stdio transport for Cursor
- Authenticates via `AIVEILIX_API_KEY` environment variable
- Implements resources (buckets, files), tools (list_buckets, query_bucket, chat_bucket)
- Uses official MCP SDK
- Run: `python -m app.mcp_stdio`

---

## 2. DATABASE SCHEMA (PostgreSQL + pgvector)

**Location**: `supabase/schema.sql` (552 lines)

### 2.1 Tables

#### 1. profiles
- Extends `auth.users` from Supabase Auth
- Columns: id (UUID, FK auth.users), email, full_name, avatar_url, timestamps
- Auto-created via trigger on signup

#### 2. buckets
- Knowledge vaults
- Columns: id, user_id, name, description, is_private, file_count, total_size_bytes, timestamps
- Automatic stats updates via triggers

#### 3. categories
- User-defined organization
- Columns: id, user_id, bucket_id, name, color, parent_id (hierarchical), timestamps

#### 4. files
- Uploaded documents
- Columns: id, user_id, bucket_id, category_id, name, original_name, mime_type, size_bytes, storage_path, status (pending/processing/ready/failed), status_message, processed_at, page_count, word_count, language, folder_path, timestamps
- Indexes: user_id, bucket_id, category_id, status

#### 5. chunks
- Extracted text pieces
- Columns: id, user_id, bucket_id, file_id, content, content_hash, chunk_index, page_number, start/end_offset, **embedding (vector(3072))**, token_count, created_at
- **Indexes**:
  - IVFFlat on embedding (vector_cosine_ops, lists=100)
  - GIN on content_tsv (full-text search)
- **Generated column**: content_tsv (tsvector)

#### 6. summaries
- AI-generated summaries
- Columns: id, user_id, bucket_id, file_id, summary_type (file/bucket/section), title, content, key_facts (JSONB), entities (JSONB), model_used, timestamps

#### 7. api_keys
- MCP access tokens
- Columns: id, user_id, name, key_hash, key_prefix, scopes (TEXT[]), allowed_buckets (UUID[]), last_used_at, request_count, is_active, expires_at, revoked_at, created_at
- Indexes: user_id, key_hash, key_prefix

#### 8. conversations
- Chat sessions
- Columns: id, user_id, bucket_id, title, mode, timestamps

#### 9. messages
- Chat messages
- Columns: id, user_id, conversation_id, role (user/assistant/system), content, model_used, tokens_used, sources (JSONB), created_at

#### 10. actions
- AI-proposed changes (future feature)
- Columns: id, user_id, conversation_id, message_id, action_type (categorize/edit_doc/delete/merge/split/tag), status, description, target_type, target_id, before_state (JSONB), after_state (JSONB), timestamps

#### 11-14. OAuth Tables
- **oauth_clients**: Client registration
- **oauth_authorization_codes**: Auth codes
- **oauth_tokens**: Access/refresh tokens
- **oauth_pkce_challenges**: PKCE support

#### 15. notifications
- User notifications
- Columns: id, user_id, type, title, message, data (JSONB), is_read, created_at

---

### 2.2 Functions

#### Search Functions
- `search_chunks(user_id, bucket_id, query, limit)`: Full-text search
- `search_chunks_semantic(user_id, bucket_id, embedding, limit)`: Vector similarity
- `full_scan_chunks(user_id, bucket_id)`: Return ALL chunks
- `match_chunks(query_embedding, bucket_id, threshold, count)`: pgvector cosine similarity

---

### 2.3 Row-Level Security (RLS)

ALL tables have RLS enabled:
- `auth.uid() = user_id` ensures users only access their data
- Enforced at database level (not application)
- Policies: SELECT, INSERT, UPDATE, DELETE for own records

---

### 2.4 Triggers

- Auto-update `updated_at` on all tables
- Auto-create profile on user signup
- Update bucket stats on file insert/delete

---

### 2.5 Migrations

Located in `supabase/migrations/`:
1. `001_add_folder_path.sql` - Folder support
2. `002_add_oauth_tables.sql` - OAuth2
3. `003_add_pkce_support.sql` - PKCE
4. `004_add_semantic_search_function.sql` - match_chunks RPC
5. `005_upgrade_to_3072_embeddings.sql` - Upgrade embeddings dimension
6. `006_create_notifications.sql` - Notifications table

---

## 3. FRONTEND ARCHITECTURE (React 18 + Vite)

### 3.1 Core Files

**`frontend/src/main.jsx`**
- React entry point, renders App into #root

**`frontend/src/App.jsx`**
- React Router v6 setup
- Routes:
  - Public: /login, /signup, /forgot-password, /terms, /privacy, /tokusho
  - Protected: /dashboard, /buckets/:id
- Wraps in ThemeProvider + AuthProvider

**`frontend/src/config.js`**
- API URL: http://localhost:7223
- Supabase URL and anon key

---

### 3.2 Pages

#### Login.jsx
- Email/password form
- Links to signup, forgot password
- Redirects to dashboard on success

#### Signup.jsx
- User registration
- Email verification flow

#### ForgotPassword.jsx
- Password reset request

#### Dashboard.jsx
Main dashboard with:
- **StatCard**: Total buckets, files, storage
- **DashboardGraph**: Activity chart (cumulative over time)
- **BucketsTable**: Bucket list with stats
- **CreateBucketModal**: Create + upload
- **ProfileModal**: Settings, password change, delete account
- **NotificationIcon**: Notification dropdown

**Features:**
- Date range picker for activity
- Theme toggle
- Create bucket with multi-file/folder upload
- Delete bucket

#### Bucket.jsx
Individual bucket view (3-column):
- **Left**: ConversationsSidebar (bucket info, new chat, conversation list)
- **Center**: ChatPanel (messages, input, AI responses)
- **Right**: FilesCard (file list, upload, preview, delete)
- File selection for chat (@mentions)

---

### 3.3 Key Components

#### ChatPanel.jsx
- Message display with timestamps, sources
- Auto-resize textarea (max 128px)
- File upload menu (files vs folders)
- Selected file chips (@mentions)
- Streaming response handling
- Conversation loading
- Web search results display

#### FilesCard.jsx
- File list with status (✅ ready, ⏳ processing, ❌ failed)
- File upload (drag-drop + click)
- Folder upload (preserves structure)
- File preview modal
- Delete confirmation

#### ConversationsSidebar.jsx
- Bucket header with back button
- "New Chat" button
- Conversation list (titles, timestamps)
- Active conversation highlighting
- Title edit, delete

#### CreateBucketModal.jsx
- Bucket name, description
- Optional file/folder upload
- Privacy toggle (UI only)

#### ProfileModal.jsx
- User info
- Change password (requires current)
- Delete account (requires password)
- Danger zone

#### NotificationIcon.jsx / NotificationDropdown.jsx
- Real-time notification display
- Mark as read
- Types: login, file_upload, file_processed, bucket_created, api_key_created

#### CreateAPIKeyModal.jsx
- Name input
- Scope selection (read, write, delete)
- Bucket restrictions
- One-time key display
- Copy to clipboard

#### DashboardGraph.jsx
- Recharts LineChart
- Cumulative files, buckets, storage over time
- Date range selection
- Responsive

---

### 3.4 Context Providers

#### AuthContext.jsx
- State: user, loading, isAuthenticated
- Methods: signup(), login(), logout(), forgotPassword()
- Token storage in localStorage: access_token, refresh_token, user
- Auto-load on mount

#### ThemeContext.jsx
- State: isDark
- Methods: toggleTheme()
- Persists to localStorage

---

### 3.5 API Service (`services/api.js`)

Axios client with:
- Base URL from config
- Request interceptor: Add Authorization header
- Response interceptor: Handle 401 (logout), errors

**API Methods:**
- `authAPI`: signup, login, logout, me, forgotPassword, changePassword, deleteAccount
- `bucketsAPI`: list, create, get, delete, deleteAll, getStats, getActivity
- `filesAPI`: list, upload, delete, getContent, updateSummary, search, semanticSearch
- `chatAPI`: sendMessage, getConversations, getMessages, updateConversation, deleteConversation
- `apiKeysAPI`: list, create, delete
- `oauthAPI`: createClient, listClients, revokeClient
- `notificationsAPI`: list, markAsRead, markAllAsRead

---

### 3.6 Styling (TailwindCSS 4)

**`frontend/tailwind.config.js`**
- Custom colors:
  - **Dark**: BG #050B0D, Text #FFFFFF, Accent #2DFFB7
  - **Light**: BG #E5F2ED, Text #050B0D, Accent #00A67E
- Glass morphism effects
- Custom animations

**Global styles** in `index.css`:
- Tailwind directives
- Custom scrollbar
- Glass cards
- Smooth transitions

---

## 4. KEY FEATURES DEEP DIVE

### 4.1 File Processing Pipeline

**Flow:**
1. Frontend: Upload → POST /api/buckets/{id}/upload
2. Backend: Save to temp → Upload to Supabase Storage → Create file record (status: processing)
3. **Async Processing**:
   - Extract text (format-specific: Vision API for images, PyMuPDF for PDFs, etc.)
   - Create chunks (150 words, 50 overlap)
   - Generate embeddings (batch OpenAI 3072-dim)
   - Store chunks with embeddings
   - Generate summary (optional/on-demand)
   - Update status (ready/failed)
4. Notifications: file_uploaded → file_processed
5. Frontend: Polls for status updates

**Supported Formats:**
- Images: All common (jpg, png, gif, bmp, webp, tiff)
- Documents: PDF, DOCX
- Data: CSV
- Code: 50+ extensions (py, js, ts, jsx, tsx, html, css, json, md, yml, etc.)

---

### 4.2 Semantic Search

**Technology:**
- Embeddings: OpenAI text-embedding-3-large (3072-dim)
- Vector DB: PostgreSQL pgvector
- Index: IVFFlat with cosine similarity (lists=100)

**Modes:**
1. **Semantic**: Vector similarity via match_chunks RPC
2. **Keyword**: Full-text search with tsvector + GIN index
3. **Hybrid**: Combines both, deduplicates, sorted by relevance

**Performance:**
- Batch embedding generation
- IVFFlat index for ANN
- Configurable limits

---

### 4.3 AI Chat System

**Architecture:**
1. **Context Building**:
   - File inventory (ALL files)
   - Summaries (comprehensive analyses)
   - Chunks (raw content, max 1000 chars each)
   - Full file fallback (if chunks < 500 chars)
   - Web search results (auto-triggered)
   - Conversation history (last 10 messages)

2. **AI Integration**:
   - Model: DeepSeek deepseek-chat
   - System prompt: Role, capabilities, rules
   - Temperature: 0.7
   - No streaming (single response)

3. **Source Tracking**:
   - Types: analysis, chunk, full_file, web_search
   - Stored in messages.sources (JSONB)
   - Displayed as citations

4. **Web Search**:
   - Auto-detection via heuristics
   - Google Custom Search API
   - Results formatted with URLs
   - Cited in response

---

### 4.4 MCP Protocol

**Two Implementations:**

#### HTTP MCP (`routers/mcp.py`)
- RESTful API
- Auth: API key via Authorization header
- Rate limiting: 100 req/hour
- Endpoints: buckets, files, query, chat

#### Stdio MCP (`mcp_stdio.py`)
- Official MCP SDK
- For Cursor
- Auth: AIVEILIX_API_KEY env var
- Resources: aiveilix://buckets/...
- Tools: list_buckets, query_bucket, chat_bucket
- Run: `python -m app.mcp_stdio`

**Security:**
- API key validation (hash, active, expiration)
- Bucket ownership check
- Scope checking (read, write, query, chat)
- Cross-user prevention
- Error sanitization

---

### 4.5 OAuth2 Integration

**Purpose**: Enable ChatGPT, Claude access

**Flow:**
1. Client registration (POST /api/oauth/clients)
2. Authorization (GET /api/oauth/authorize)
3. User approval → redirect with code
4. Token exchange (POST /api/oauth/token)
5. Access via MCP endpoints with token
6. Refresh (grant_type=refresh_token)
7. Revocation (delete client)

**Security:**
- PKCE support
- SHA-256 hashing
- Access tokens: 60 min
- Refresh tokens: 30 days
- One-time auth codes (10 min)

---

### 4.6 Notifications System

**Types:**
- login: "Welcome back!"
- file_uploaded: "File {name} uploaded"
- file_processed: "File {name} ready"
- bucket_created: "Bucket {name} created"
- api_key_created: "API key {name} created"

**Implementation:**
- Backend creates via notifications service
- Frontend polls GET /api/notifications
- NotificationIcon shows unread count
- Dropdown shows recent
- Mark as read
- Stored in notifications table (JSONB data)

---

## 5. DATA FLOW EXAMPLES

### 5.1 User Signup & Login
```
Signup:
1. Frontend: Form → POST /api/auth/signup
2. Backend: Supabase Auth creates user
3. Database: Trigger creates profile
4. Frontend: Email verification required

Login:
1. Frontend: Form → POST /api/auth/login
2. Backend: Supabase Auth validates
3. Backend: Create login notification
4. Response: access_token, refresh_token, user
5. Frontend: Store in localStorage
6. Frontend: Redirect to /dashboard
```

### 5.2 File Upload & Chat
```
Upload:
1. User drops file → POST /api/buckets/{id}/upload
2. Backend: Save to Supabase Storage
3. File record (status: processing)
4. Async: Extract → Chunk → Embed → Store
5. Status: ready/failed
6. Notifications: file_uploaded → file_processed

Chat:
1. User: "What is this file about?"
2. POST /api/buckets/{id}/chat
3. Backend:
   - Get files (inventory)
   - Get summaries (analyses)
   - Get chunks (raw)
   - Fallback: full file if chunks < 500 chars
   - Web search: check if needed
4. Build context: inventory + analyses + chunks + web
5. Call DeepSeek with context + history
6. Save messages
7. Return with sources
8. Frontend: Display with citations
```

### 5.3 MCP API Key Usage
```
Create:
1. User: API Keys modal → POST /api/api-keys
2. Backend: Generate aiveilix_sk_live_<random>
3. Hash with SHA-256, store hash + prefix
4. Return full key ONCE
5. User copies to Cursor config

Use:
1. Cursor: GET /mcp/buckets with Authorization: Bearer <key>
2. Backend: Hash key, check DB
3. Validate: active, not expired, rate limit
4. Check allowed_buckets
5. Return bucket list
6. Update last_used_at, request_count
```

---

## 6. CONFIGURATION & DEPLOYMENT

### 6.1 Environment Variables

**Backend** (`.env` in project root):
```env
# Supabase
SUPABASE_URL=https://eaeerftdgpkaitxtpluu.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
DATABASE_URL=postgresql://postgres:...@db.eaeerftdgpkaitxtpluu.supabase.co:5432/postgres

# AI APIs
DEEPSEEK_API_KEY=sk-...     # Chat
OPENAI_API_KEY=sk-...        # Embeddings + Vision
GEMINI_API_KEY=...           # Fallback

# Google Search
GOOGLE_SEARCH_API_KEY=...
GOOGLE_SEARCH_CX=...

# App
APP_ENV=development
APP_SECRET_KEY=...
```

**Frontend** (Vite env vars):
```env
VITE_API_URL=http://localhost:7223
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
```

### 6.2 Running the Application

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```
Runs on http://localhost:7223

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Runs on http://localhost:6677

**Database:**
- Create Supabase project
- Enable pgvector extension
- Run schema.sql
- Create "files" storage bucket (private)
- Add storage RLS policies

---

## 7. TECHNICAL HIGHLIGHTS

### 7.1 Advanced Features

1. **Intelligent File Processing**:
   - GPT-4o Vision for images + PDF embedded images
   - 50+ file types support
   - Encoding detection + fallback
   - Binary rejection with clear errors

2. **Precision Semantic Search**:
   - 3072-dim embeddings (highest quality)
   - Batch generation
   - Hybrid search
   - IVFFlat indexing

3. **Smart Context Building**:
   - Full file fallback when chunks insufficient
   - File inventory awareness
   - Summaries + chunks
   - Web search auto-triggering

4. **Production Security**:
   - Row-level security (database)
   - API key hashing (SHA-256)
   - OAuth2 with PKCE
   - Rate limiting
   - Error sanitization
   - Cross-user prevention

5. **Developer Experience**:
   - Colored logging
   - Error tracking (error_id, traceback)
   - Request/response logging
   - Hot reload

6. **MCP Protocol**:
   - Official SDK
   - HTTP + stdio
   - ChatGPT/Cursor ready
   - Unified auth (OAuth2 + API keys)

---

### 7.2 Performance Optimizations

1. **Batch Operations**:
   - Batch embedding generation (2048 inputs/request)
   - Batch chunk insertion

2. **Intelligent Caching**:
   - On-demand summary generation
   - Full file caching in Supabase Storage

3. **Database Indexes**:
   - IVFFlat for vector search
   - GIN for full-text
   - B-tree on foreign keys
   - Compound indexes

4. **Async Processing**:
   - File processing doesn't block upload
   - Status polling for UI

---

### 7.3 Code Quality

1. **Comprehensive Logging**:
   - Structured with levels
   - Color-coded
   - Request/response tracking
   - Error IDs

2. **Error Handling**:
   - Try-catch everywhere
   - Specific error messages
   - Fallback strategies
   - User-friendly responses

3. **Type Safety**:
   - Pydantic models
   - TypeScript-ready structure

4. **Clean Architecture**:
   - Separation of concerns
   - Reusable components
   - DRY principle
   - Single responsibility

---

## 8. FUTURE ENHANCEMENTS

1. Live Agent: Silent monitoring + error fixing
2. Project Management: Track AI agent projects
3. Collaborative Buckets: Share with others
4. Advanced Filters: Date, type, category
5. Export: Chat history, summaries
6. Webhooks: Event notifications
7. OCR for PDFs: Enhanced extraction
8. Audio/Video: Transcription support
9. Multi-language: i18n support
10. Privacy Toggle: Public/private buckets

---

## 9. FILE LOCATIONS (Absolute Paths)

**Backend:**
- Entry: `/Volumes/KIOXIA/AIveilix/backend/run.py`
- Main: `/Volumes/KIOXIA/AIveilix/backend/app/main.py`
- Config: `/Volumes/KIOXIA/AIveilix/backend/app/config.py`
- Routers: `/Volumes/KIOXIA/AIveilix/backend/app/routers/`
- Services: `/Volumes/KIOXIA/AIveilix/backend/app/services/`
- Models: `/Volumes/KIOXIA/AIveilix/backend/app/models/`

**Frontend:**
- Entry: `/Volumes/KIOXIA/AIveilix/frontend/src/main.jsx`
- App: `/Volumes/KIOXIA/AIveilix/frontend/src/App.jsx`
- Pages: `/Volumes/KIOXIA/AIveilix/frontend/src/pages/`
- Components: `/Volumes/KIOXIA/AIveilix/frontend/src/components/`
- API: `/Volumes/KIOXIA/AIveilix/frontend/src/services/api.js`

**Database:**
- Schema: `/Volumes/KIOXIA/AIveilix/supabase/schema.sql`
- Migrations: `/Volumes/KIOXIA/AIveilix/supabase/migrations/`

**Docs:**
- Walkthrough: `/Volumes/KIOXIA/AIveilix/PROJECT_WALKTHROUGH.md`
- Instructions: `/Volumes/KIOXIA/AIveilix/CLAUDE.md`

---

## 10. QUICK REFERENCE

### Port Numbers
- Backend API: **7223**
- Frontend: **6677**

### Key Technologies
- **Backend**: FastAPI, Python 3.14, Pydantic, Uvicorn
- **Frontend**: React 18, Vite, TailwindCSS 4, Axios, React Router v6, Recharts
- **Database**: PostgreSQL, pgvector, Supabase
- **AI**: DeepSeek (chat), OpenAI (embeddings + GPT-4o Vision), Gemini (fallback)
- **Search**: Google Custom Search API
- **Auth**: Supabase Auth, JWT tokens
- **Storage**: Supabase Storage
- **Protocol**: MCP (HTTP + stdio)

### Important Notes
- **Vector embeddings**: 3072 dimensions (OpenAI text-embedding-3-large)
- **Chunking**: 150 words with 50-word overlap
- **Rate limiting**: 100 requests/hour on MCP endpoints
- **JWT auth**: Access + refresh tokens in localStorage
- **RLS**: Enforced at database level for all tables
- **File storage**: Supabase Storage at `user_id/bucket_id/uuid.ext`
- **API key format**: `aiveilix_sk_live_<32-byte-random>`
- **OAuth tokens**: Access 60 min, refresh 30 days

---

# Rules
**ts** = tell me in short. If user command contains "ts", make response real short but clear.

---

This comprehensive knowledge base covers the entire AIveilix codebase architecture, implementation details, data flows, and technical specifications. The system is production-ready with enterprise-grade security, advanced AI capabilities, and exceptional developer experience.
