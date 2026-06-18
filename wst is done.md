# What Is Done

## 2026-04-01

### Documentation reviewed

- Read all main docs in `AIEILIX=DOC/docs`
- Added and reviewed `agent.md`
- Updated docs from `Redis` to `Valkey`
- Added `db-progress.md`

### PostgreSQL

- Created local PostgreSQL workspace under `backend/database/postgres`
- Added full bootstrap schema migration
- Created local start / apply / stop scripts
- Started local PostgreSQL
- Created database `aiveilix`
- Applied schema successfully
- Verified all main tables and enums

### PostgreSQL schema includes

- users
- profiles
- buckets
- categories
- files
- file_versions
- chunks
- summaries
- conversations
- messages
- conversation_chunks
- oauth_authorization_codes
- oauth_tokens
- api_keys
- team_members
- team_bucket_access
- team_activity_log
- subscriptions
- api_usage
- usage_tracking
- notifications
- investigation_events
- error_logs

### Qdrant

- Created local Qdrant workspace under `backend/database/qdrant`
- Added bootstrap script for collections
- Added local setup / bootstrap / verify scripts
- Created collections:
  - `text_chunks`
  - `image_chunks`
  - `conversation_chunks`
- Verified collections exist

### Qdrant compatibility

- Found version mismatch between backend and database tooling
- Updated backend to `qdrant-client==1.17.1`
- Aligned database tooling to the same version
- Verified backend can open the local embedded Qdrant store
- Verified backend can read all three Qdrant collections

### Valkey

- Created local Valkey workspace under `backend/database/valkey`
- Added local config file
- Added local start / verify / stop scripts
- Defined key strategy for:
  - refresh tokens
  - JWT blacklist
  - failed login rate limiting
  - password reset tokens
  - email verification tokens
  - cache
  - file processing queues
  - embedding queues
  - conversation embedding queue
- Started local compatible server on port `6380`
- Verified ping and key read/write

### Backend config integration

- Wired `QDRANT_PATH` into backend settings
- Added backend Qdrant client factory for local path or host/port mode
- Confirmed `QDRANT_PATH` resolves to the local embedded store

### Backend DB connections

- Added PostgreSQL live connection check in backend app code
- Added Qdrant live connection check in backend app code
- Added Valkey live connection check in backend app code
- Added shared backend health service for dependency status
- Updated FastAPI lifespan startup to verify DB dependencies before serving requests
- Removed fake `Base.metadata.create_all()` startup behavior
- Started backend successfully with dependency checks enabled
- Verified live `/health` response shows:
  - PostgreSQL `ok`
  - Qdrant `ok`
  - Valkey `ok`

### Current state

- PostgreSQL local setup is working
- Qdrant local setup is working
- Valkey local setup is working
- Backend Qdrant path compatibility issue is fixed
- Backend infrastructure is connected to all three stores

### Pipeline handoff

- Added pipeline build brief for a dedicated third agent:
  - `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/pipeline-agent-plan.md`

### Internal agent handoff

- Added detailed builder brief for internal Aiveilix agent:
  - `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/agent-builder-plan.md`
- Added short pointer note:
  - `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/agent-builder-quick-note.md`

### File pipeline implementation

- Added pipeline SQLAlchemy models:
  - `app/models/file.py`
  - `app/models/chunk.py`
  - `app/models/investigation_event.py`
  - `app/models/error_log.py`
- Added file schemas:
  - `app/schemas/files.py`
- Added storage service:
  - `app/services/storage/r2.py`
- Added retry helper:
  - `app/services/pipeline/retry.py`
- Added upload intake service:
  - `app/services/pipeline/upload.py`
- Added pipeline orchestrator:
  - `app/services/pipeline/orchestrator.py`
- Added processing services:
  - `app/services/processing/docling_service.py`
  - `app/services/processing/gemini_service.py`
  - `app/services/processing/layout_builder.py`
  - `app/services/processing/chunker.py`
- Added embedding services:
  - `app/services/embeddings/text_embeddings.py`
  - `app/services/embeddings/image_embeddings.py`
- Added Qdrant file indexer:
  - `app/services/qdrant/file_indexer.py`
- Implemented file API routes in:
  - `app/api/v1/endpoints/files.py`
- Updated startup to call Qdrant collection ensure logic
- Added package requirements:
  - `open-clip-torch==2.26.1`
  - `tiktoken==0.7.0`

### File pipeline implemented flow

- `POST /v1/buckets/{bucket_id}/files`
  - saves raw file to R2
  - creates `files` row
  - creates `file_versions` row
  - moves file status to `processing`
  - writes investigation events
  - pushes file id to Valkey queue
  - triggers background processing
- background processing flow:
  - download raw file from R2
  - Docling extraction
  - Gemini visual extraction
  - Layout JSON build
  - Layout JSON upload to R2
  - chunk generation
  - chunk rows written to PostgreSQL
  - BGE-M3 text embeddings
  - CLIP image embeddings
  - Qdrant upsert for text and image collections
  - file status set to `ready`
- failure flow:
  - file status set to `failed`
  - `error_logs` row written
  - `investigation_events` failure row written

### File pipeline bug fixes (2026-04-01)

All four review-identified bugs are now fixed:

**1. JWT field fixed**
- `current_user["sub"]` → `current_user["user_id"]` in all file endpoints
- Matches the actual payload set by `security.create_access_token()`

**2. Bucket ownership auth added**
- Added `_require_owned_bucket(db, bucket_id, user_id)` helper
- Every file endpoint now queries `Bucket.user_id == current_user["user_id"]` before proceeding
- Returns 404 if bucket doesn't exist, 403 if the user doesn't own it

**3. Qdrant collection schema fixed**
- `file_indexer.py` now matches `bootstrap_collections.py` exactly:
  - `text_chunks`: unnamed dense vector (bare `VectorParams`) + sparse named `"text_sparse"`
  - `image_chunks`: unnamed dense vector (bare `VectorParams`, no named-vector dict)
- Upsert payload keys updated to match (`text_sparse` instead of `sparse`, bare list for image dense vector)

**4. `upload_started` event fixed**
- File row is now created and flushed first to obtain the file UUID
- `upload_started` event is logged immediately after `db.flush()` with the real `file_id`
- R2 upload happens after the event is logged
- Full event sequence is now: `upload_started → upload_completed → file_processing_queued`

### Frontend

- Created frontend project scaffold under `frontend`
- Set up React + Vite
- Set up Tailwind CSS
- Added base frontend files and starter app shell
- Added frontend `.env` with `PORT=9087`
- Configured Vite to use the env port
- Installed frontend dependencies
- Verified the frontend dev server starts on port `9087`
- Added `react-router-dom`
- Built frontend auth routes:
  - `/login`
  - `/signup`
  - `/forgot-password`
- Added login page with email/password and Google/GitHub entry buttons
- Added create account page with name, email, password, Google/GitHub entry buttons, and legal text
- Added forgot password page with email input and reset action
- Added confirm email page shown after email signup
- Added confirm email timer flow:
  - shows entered name and email
  - starts at 120 seconds
  - resend resets timer to 120 seconds
- Rebuilt onboarding flow after auth
- Updated login flow to go to onboarding
- Updated confirm email flow to go to onboarding
- Reworked onboarding UI using 21st.dev-inspired staged onboarding structure
- Added `lottie-react` for onboarding illustration
- Replaced the previous Rive-based illustration with a custom local Lottie animation
- Dashboard remains the final handoff page after onboarding
- Added light and dark mode toggle across auth pages
- Verified frontend production build succeeds

### Auth system

- Built SQLAlchemy models: `User`, `Profile`, `OAuthToken`
- Built Pydantic schemas for all auth flows (register, login, 2FA, OAuth, password reset, refresh, logout)
- Built core security utilities:
  - JWT create/verify/decode (access token 24hrs, refresh 30 days, temp 10min)
  - bcrypt password hash/verify (cost 12)
  - TOTP 2FA generate/verify (pyotp)
  - backup codes generator (8 codes)
- Built full auth service (`app/services/auth.py`):
  - Register with email verification token stored in Valkey
  - Login with rate limiting (5 attempts/hr via Valkey)
  - 2FA verify (TOTP + backup codes)
  - Enable / confirm / disable 2FA
  - Refresh token (stored in Valkey, 30 days TTL)
  - Logout with JWT blacklist in Valkey
  - Forgot password (reset token in Valkey, 1hr TTL)
  - Reset password
  - Google OAuth
  - GitHub OAuth
- Built JWT middleware (`app/api/v1/deps.py`): validates JWT + checks Valkey blacklist
- Wired all 13 auth endpoints to real service logic

### Frontend ↔ Backend connection

- Added `VITE_API_URL=http://localhost:4565` to `frontend/.env`
- Created `frontend/src/api/auth.js` — centralized API service layer:
  - `authApi.register(fullName, email, password)`
  - `authApi.login(email, password)`
  - `authApi.forgotPassword(email)`
  - `authApi.resendVerification(email)`
- Added `POST /auth/resend-verification` backend endpoint (was missing)
  - Added `ResendVerificationRequest/Response` schemas
  - Added `resend_verification()` service function
  - Wired to router (now 14 auth endpoints total)
- Rewrote `frontend/src/App.jsx` — all auth pages now wired to real API:
  - **LoginPage**: calls `authApi.login()`, stores `access_token` in sessionStorage and `refresh_token` in localStorage, redirects to `/dashboard` or `/2fa?temp_token=...` for 2FA
  - **SignupPage**: calls `authApi.register()`, redirects to `/confirm-email?name=...&email=...`
  - **ConfirmEmailPage**: calls `authApi.resendVerification()` on resend, resets 120s timer on success
  - **ForgotPasswordPage**: calls `authApi.forgotPassword()`, shows success message
  - All forms: loading states, inputs disabled during request, error/success alerts
  - Added `Alert` component for inline error and success messages

### Bug fixes

- Fixed CORS: `FRONTEND_URL` was `localhost:5173`, changed to `localhost:9087` (actual frontend port)
- Fixed `provider_enum` → `auth_provider` and `theme_enum` → `theme_mode` in SQLAlchemy models to match DB schema
- Fixed Gmail app password stored with spaces — removed spaces so SMTP auth works

### Email (SMTP)

- Created `app/services/email.py` with `send_verification_email()` and `send_password_reset_email()`
- Wired email sending into `register()`, `resend_verification()`, `forgot_password()` — all 3 TODOs replaced
- Configured SMTP with personal Gmail app password (chaffanjutt313@gmail.com) — working and verified
- Verification email includes styled button linking to `/verify-email?token=...`
- Password reset email includes styled button linking to `/reset-password?token=...`

### Current state

- Registration creates account and sends real verification email ✓
- Resend verification sends new email ✓
- Forgot password sends real reset email ✓
- Full auth flow is end-to-end working

### Password reset flow (code-based)

- Changed reset token from UUID link to **6-digit numeric code**
- Backend `forgot_password()` now generates `random.randint(100000, 999999)` and stores as `password_reset:{code}` in Valkey (1hr TTL)
- Updated `send_password_reset_email()` to email the code directly (styled large code block, no link)
- `reset_password()` endpoint unchanged — accepts `token` (now the 6-digit code) + `new_password`
- Added `authApi.resetPassword(code, newPassword)` to `frontend/src/api/auth.js`
- Rewrote `ForgotPasswordPage` in `App.jsx` as a 3-step flow on one page:
  - Step 1: email input → Send Code button
  - Step 2: code field appears → auto-advances to step 3 when all 6 digits entered
  - Step 3: new password field appears → Reset Password button → redirects to login on success
  - On wrong code: error shown, resets back to step 2

### Next likely steps

- Build user profile endpoints (GET/PATCH)
- Build bucket endpoints (create, list, get, delete)
- Build file upload endpoints (upload to R2, store metadata in DB)

## 2026-04-01 Agent implementation review

### What was checked

- Reviewed the newly added internal agent backend path:
  - `backend/app/services/agent/service.py`
  - `backend/app/services/agent/retrieval.py`
  - `backend/app/services/agent/llm.py`
  - `backend/app/services/agent/web.py`
  - `backend/app/api/v1/endpoints/conversations.py`
  - `backend/app/api/v1/endpoints/search.py`
  - `backend/app/schemas/agent.py`
  - `AIEILIX=DOC/docs/agent-builder-implementation.md`

### What is confirmed working

- Conversation routes, search routes, and agent service layer are implemented
- User/bucket/conversation ownership checks are present in the agent service
- Message memory is persisted into PostgreSQL `conversation_chunks`
- Best-effort Qdrant upsert for conversation memory is implemented
- Agent code compiles/imports cleanly

### Important review findings

- Bucket retrieval is **not** the planned Qdrant hybrid/vector search yet
  - current code retrieves `Chunk` rows from PostgreSQL and ranks them with text matching in `search_bucket_documents()`
  - this is a working first version, but not the planned full RAG retrieval layer
- Conversation memory retrieval is also **not** using Qdrant search
  - memory embeddings are written to Qdrant, but retrieval currently reads from PostgreSQL `conversation_chunks` and scores text locally
- `/buckets/{bucket_id}/query` follow-up behavior is incomplete compared to thread chat
  - it sets `follow_up_required=true` but still returns a normal answer instead of asking the follow-up question directly
- Source rendering always adds a `Sources:` block, but when nothing external is used it shows `No external sources used.`
  - this should be confirmed against the final product rule for source display

### Current verdict

- The internal agent is **built in version 1 form**
- It is **not fully implemented exactly as planned**
- Biggest remaining gap: true Qdrant/hybrid document retrieval and memory retrieval

## 2026-04-01 Pipeline fix verification

### Verified fixes

- `backend/app/api/v1/endpoints/files.py`
  - `current_user["sub"]` is gone
  - file routes now use JWT `user_id`
  - bucket ownership check is present through `_require_owned_bucket(...)`
- `backend/app/services/pipeline/upload.py`
  - `upload_started` is now logged after the file row exists and has a real `file_id`

### Qdrant payload index fix (complete)

- `backend/app/services/qdrant/file_indexer.py` — `ensure_collections()` now fully matches `bootstrap_collections.py`:
  - `text_chunks` payload indexes: `file_id`, `bucket_id`, `page`, `status`, `nearby_image_id`
  - `image_chunks` payload indexes: `file_id`, `bucket_id`, `page`, `image_id`, `nearby_text_id`, `status`
  - Indexes are created on every startup, outside the collection-creation block
  - Duplicate index errors are silently ignored — same idempotent behaviour as the bootstrap script
  - Added `_ensure_payload_indexes()` private helper

### Final verdict — all 4 fixes confirmed complete

- JWT field: `user_id` ✓
- Bucket ownership auth: `_require_owned_bucket()` ✓
- Qdrant collection schema + payload indexes: fully matches bootstrap ✓
- `upload_started` event order: logged after file row flush ✓

## 2026-04-01 Agent retrieval verification

### Verified agent-side fixes

- `backend/app/services/agent/retrieval.py`
  - bucket retrieval now queries Qdrant `text_chunks`
  - hybrid dense+sparse retrieval is attempted first when sparse weights are available
  - dense-only fallback is present
  - conversation memory retrieval now queries Qdrant `conversation_chunks`
  - source fallback wording is now:
    - `Sources:`
    - `No document or web sources were used.`
- `backend/app/services/agent/service.py`
  - `/buckets/{bucket_id}/query` now returns the follow-up question directly when clarification is needed
- `AIEILIX=DOC/docs/agent-builder-implementation.md`
  - implementation note was updated to match the new retrieval path

### New review finding

- `backend/app/services/agent/service.py`
  - conversation memory persistence still appears wrong for Qdrant
  - `_persist_message_memory()` uses `embed_texts(memory_parts)` and then writes each returned item directly as `PointStruct(vector=vector)`
  - but `embed_texts()` returns a dict with `dense` and `sparse`, not a plain dense vector
  - current `conversation_chunks` collection setup in this service only creates a dense vector config
  - likely result: Qdrant upsert for conversation memory can fail, which would leave thread-memory retrieval empty even though retrieval now points at Qdrant

### Current verdict

- doc retrieval fix: in place
- follow-up fix: in place
- source-block fix: in place
- conversation memory retrieval path: in place
- conversation memory Qdrant persistence: still needs one more fix

## 2026-04-01 Agent memory persistence verification

### Confirmed fix

- `backend/app/services/agent/service.py`
  - `_persist_message_memory()` no longer writes the hybrid embedding dict directly into the dense-only `conversation_chunks` collection
  - it now extracts only each row's dense vector from the BGE embedding result
  - if that path fails, it falls back to the local dense embedder from `backend/app/services/embeddings/service.py`
  - `PointStruct(vector=...)` now matches the collection schema

### Final agent review verdict

- document retrieval: fixed
- follow-up behavior: fixed
- source block behavior: fixed
- conversation memory retrieval: fixed
- conversation memory persistence: fixed

### Verification

- `backend/venv/bin/python -m compileall backend/app` passed

## 2026-04-01 Repo safety

- Created root `.gitignore`
- Added ignores for:
  - `.env`
  - `backend/.env`
  - Python caches and virtualenvs
  - frontend build/runtime folders
  - local temp/cache folders
  - local Qdrant, Valkey, and Postgres dev data/log artifacts

## 2026-04-01 Onboarding rebuild

- Deleted old heavy multi-step onboarding UI (FlowShell, OptionCard, InfoRow, OnboardingIllustration, StageChip, Lottie imports)
- Rebuilt as a small centered modal popup (`OnboardingModal` in `App.jsx`)
- 3 questions shown one at a time with row-style option buttons (no icons, minimal)
- Progress dots at the bottom + Back and Skip buttons on every step
- Card style matches the auth card (same background, border, shadow)
- On completion: calls `authApi.saveOnboarding()` → `POST /user/onboarding`
- Sets `aiveilix-onboarded` in localStorage so modal never shows again on return
- Login redirects to `/onboarding` if flag not set, else directly to `/dashboard`

### Backend for onboarding

- Created `app/services/profile.py` with `save_onboarding(db, user_id, use_case, need, referral_source)`
- Saves `use_case`, `bio` (from `need`), and `referral_source` fields on the `profiles` row
- Added `POST /user/onboarding` endpoint in `app/api/v1/endpoints/users.py`
- Added `use_case` and `referral_source` columns to profiles:
  - Migration file: `backend/database/postgres/migrations/2026-04-01_add_onboarding_to_profiles.sql`
  - Run: `ALTER TABLE profiles ADD COLUMN IF NOT EXISTS use_case TEXT, ADD COLUMN IF NOT EXISTS referral_source TEXT;`
- Added `use_case: Mapped[str | None]` and `referral_source: Mapped[str | None]` to `Profile` SQLAlchemy model

## 2026-04-01 Dashboard — backend

- Created `app/services/dashboard.py` with:
  - `get_profile()` — returns full_name, avatar_url from profiles
  - `get_stats()` — storage_gb, files_count, chat_messages, mcp_calls, bucket_count (live counts)
  - `get_monthly_stats()` — last 6 months from usage_tracking table
  - `list_buckets()` — all user buckets with per-bucket file count
  - `create_bucket()` — creates Bucket row, generates `mcp_token` via `secrets.token_urlsafe(32)`
  - `list_notifications()` — last 20 notifications ordered by created_at
  - `mark_all_notifications_read()` — sets `is_read=True` on all unread notifications
- Created `app/models/notification.py` — Notification SQLAlchemy model (id, user_id, type, title, message, is_read, created_at)
- Created `app/models/usage.py` — UsageTracking SQLAlchemy model (id, user_id, month, storage_used, chat_messages_count, mcp_calls_count, buckets_count, files_count)
- Implemented `GET /user/profile`, `GET /user/stats`, `GET /user/stats/monthly` in `users.py`
- Implemented `GET /buckets`, `POST /buckets` in `buckets.py`
- Implemented `GET /notifications`, `PUT /notifications/read-all` in `notifications.py`

## 2026-04-01 Dashboard — frontend

- Added `dashboardApi` to `frontend/src/api/auth.js`:
  - `getProfile()`, `getStats()`, `getMonthlyStats()`, `listBuckets()`, `createBucket()`, `listNotifications()`, `markAllRead()`
  - All calls use `authToken()` from sessionStorage
- Built full `DashboardPage` in `App.jsx`:
  - Sticky top nav: welcome message (user's name), dark/light toggle, notification bell with dropdown, profile icon
  - Notifications dropdown: shows last 20 notifications, "Mark all read" button
  - 4 metric cards: Storage Used, Files, Chat Messages, MCP Calls
  - Full-width Activity Overview multiline chart (see below)
  - Bucket grid: shows all user buckets with file count, color dot, name, description
  - "Create New Bucket" button opens modal
  - Create bucket modal: name, description, color picker (6 options), icon picker (8 options) — calls `POST /buckets`
  - All data fetched from real backend on mount

## 2026-04-01 Activity Overview chart

- Removed two separate bar charts (storage bar + MCP calls bar)
- Built `MultiLineChart` SVG component — full-width, 3 lines: Buckets (green), Files (purple), Storage GB (blue)
- Each series normalized to its own max so all 3 lines are always visible regardless of magnitude difference
- Legend shows series name + current (latest month) value in matching color
- Month labels on X-axis (e.g. "Apr '26"), subtle horizontal grid lines
- Loading skeleton + "No activity data yet" empty state
- Chart height 340px (increased from 220px at user request)
- Placed full-width between metric cards and bucket grid in `DashboardPage`
- Backend: `get_monthly_stats()` updated to include `"buckets"` field (from `buckets_count`) per month

## 2026-04-01 LLM provider config

- Updated backend provider config to support:
  - `auto`
  - `claude`
  - `gemini`
  - `openai`
  - `deepseek`
  - `kimi`
- Added `DEEPSEEK_API_KEY` and `DEEPSEEK_BASE_URL` to backend settings
- Updated provider selection so `LLM_PROVIDER=auto` picks the first configured provider
- Added placeholder env keys for:
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`
  - `DEEPSEEK_API_KEY`
  - `DEEPSEEK_BASE_URL`
  - `MOONSHOT_API_KEY`
  - `MOONSHOT_BASE_URL`
- Updated root `.env` and `backend/.env.example`
- Verification:
  - `backend/venv/bin/python -m compileall backend/app` passed
  - provider selection check returned `auto` -> `gemini` with the current local env

## 2026-04-01 Dashboard polish + profile popup

### Dashboard UI updates

- Updated dashboard visual styling in `frontend/src/App.jsx`
  - navbar background blended into the page background
  - controls and metric areas made larger and softer
  - text shifted from gray-heavy styling to black/white-first styling
  - overly rounded shapes reduced across the dashboard
  - dashboard made vertically scrollable
- Cleaned top-right actions
  - switched to cleaner outline icons
  - moved `Create Bucket` under the top-right actions
  - adjusted button width/position multiple times to align with metric layout
- Removed the old dashboard title block:
  - removed `Aiveilix`
  - removed `Knowledge Dashboard`

### Profile popup UI

- Built a large centered profile popup modal in `frontend/src/App.jsx`
- Reworked it from a side slider into a true popup modal
- Removed the fake top tabs (`Security`, `Preferences`, `Billing`, `Danger Zone`) from the top nav
- Final popup now uses one single settings flow with sections inside:
  - profile/avatar
  - name + email
  - change password
  - appearance/theme
  - billing
  - danger zone
- Simplified the popup layout:
  - removed heavy stacked card look
  - reduced border noise
  - flattened the content into cleaner sections

### Profile popup backend wiring

- Implemented real profile actions:
  - `PUT /user/profile`
  - `PUT /user/avatar`
  - `PUT /user/password`
  - `DELETE /user/account`
- Extended `backend/app/services/profile.py` to support:
  - full profile fetch payload
  - profile update
  - avatar upload
  - password change
  - account deletion
- Avatar upload supports:
  - R2 public upload when configured
  - data URL fallback for local/dev if R2 public config is missing

### Buckets table

- Replaced bucket card grid with a table layout in `frontend/src/App.jsx`
- Table columns:
  - `Name`
  - `Created At`
  - `Files`
  - `Storage`
  - `Actions`
- Storage formatting rules:
  - show `MB` when under `1 GB`
  - show `GB` when `1 GB` or more
- Added responsive horizontal scroll support for the table on smaller screens

### Bucket actions backend

- Added `DELETE /buckets/all` usage in the popup danger zone
- Implemented single bucket delete:
  - backend service: `delete_bucket()` in `backend/app/services/dashboard.py`
  - endpoint: `DELETE /buckets/{bucket_id}` in `backend/app/api/v1/endpoints/buckets.py`
- Added row delete action in the new bucket table UI

### Frontend API updates

- Extended `dashboardApi` in `frontend/src/api/auth.js` with:
  - `updateProfile()`
  - `uploadAvatar()`
  - `changePassword()`
  - `deleteAccount()`
  - `deleteAllBuckets()`
  - `deleteBucket()`

### Verification

- `npm run build` passed in `frontend`

## 2026-04-01 Bucket composer radius tweak

- Increased the rounding on the bucket page input/composer bar

### Verification

- `npm run build` passed in `frontend`

## 2026-04-01 Bucket thread row tightening

- Removed the `x/20 threads` usage text from the bucket sidebar
- Added limit warning only when the thread count reaches the cap:
  - `Thread limit reached`
- Made each thread bubble shorter/tighter
- Kept thread row content to one line:
  - title
  - last open time

### Verification

- `npm run build` passed in `frontend`

## 2026-04-01 Bucket composer cleanup

- Removed the divider line above the bucket page input/composer bar

### Verification

- `npm run build` passed in `frontend`

## 2026-04-01 Bucket page follow-up cleanup

- Removed the top chat header block from the bucket page center area:
  - removed `Onboarding notes`
  - removed `Bucket chat workspace`
- Removed the large rounded center chat card shell so the chat area sits directly on the page

### Verification

- `npm run build` passed in `frontend`

## 2026-04-01 Bucket thread list cleanup

- Updated left thread list UI in `frontend/src/App.jsx`
- Each thread row now shows:
  - title
  - last open time on the same line
- Removed:
  - subtitle/preview line
  - separate last-used line
- Added hover `...` menu per thread with UI actions:
  - rename
  - pin / unpin
  - delete
- Kept thread creation limit at 20 in the bucket UI

### Verification

- `npm run build` passed in `frontend`

## 2026-04-01 Bucket sidebar card cleanup

- Removed the divider line under the header area in the bucket side panels
- Applied to both:
  - left thread/sidebar card
  - right files/sidebar card

### Verification

- `npm run build` passed in `frontend`
- `backend/venv/bin/python -m py_compile` passed for touched backend files

## 2026-04-01 Dashboard follow-up polish

### Buckets table

- Replaced the small bucket cards in the dashboard with a row-based table UI
- Table columns now:
  - `Name`
  - `Created At`
  - `Files`
  - `Storage`
  - `Actions`
- Storage display updated:
  - shows `MB` when below `1 GB`
  - shows `GB` when `1 GB` or higher
- Added per-row delete action connected to backend bucket deletion
- Added horizontal overflow handling so the table still works on smaller widths

### Create bucket popup

- Increased popup size
- Converted description field to multiline textarea
- Removed color picker section from the popup
- Fixed light mode popup styling:
  - lighter overlay in light mode
  - solid white modal surface in light mode
  - removed dark tinted background look in light mode

### Verification

- `npm run build` passed in `frontend`

## 2026-04-01 Bucket page UI shell

### New bucket route

- Added bucket workspace route in `frontend/src/App.jsx`
  - `GET /bucket/:bucketId` frontend route only
- Wired dashboard bucket name click to open the new bucket page

### Bucket page layout

- Built initial bucket page UI shell in `frontend/src/App.jsx`
- 3-column layout:
  - left thread sidebar
  - center chat area
  - right files sidebar
- Both side panels are collapsible

### Left sidebar

- Added:
  - back to dashboard button
  - thread list UI
  - new thread button
  - thread usage display
- Thread creation limited to **20 threads** in UI

### Center chat area

- Added chat message area in the center
- Added ChatGPT-style composer:
  - left `+`/attachment button
  - right send button
  - uploaded files shown as chips
  - input starts as single-line
  - textarea auto-grows into multiline when content expands

### Right files sidebar

- Added files list panel UI
- Shows uploaded file rows in a tall rounded side panel

### Theme support

- Bucket page UI supports both dark and light theme

### Verification

- `npm run build` passed in `frontend`
