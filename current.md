# AIveilix – Current State Checkpoint

> Purpose: get brutally honest clarity about where AIveilix actually is **right now** (based on real code).
> This is a “living” checkpoint you can keep updated as you ship.

---

## How this works (important)
- This file reflects the repo as it exists **today**.
- It calls out **what’s built**, **what’s missing**, and **what’s risky** (security/reliability).

---

## 1. Project Identity (Reality Check)
- **One sentence**: AIveilix is a full‑stack knowledge-bucket platform where users upload documents and then **chat/search** across them, plus expose data via **MCP**.
- **Primary users**: Individuals (and eventually teams) who want “ChatGPT for my documents” with organized buckets + API access.
- **What it does better**: Buckets + API keys + MCP integration in the same product (UI + programmatic access).
- **Type**: Product / startup-ready prototype (core features exist, some integrations are incomplete).

---

## 2. Repo / Folder Structure
- **Top-level**
  - `backend/` FastAPI server
  - `frontend/` React (Vite + Tailwind) UI
  - `supabase/` schema + migrations (pgvector, oauth tables, etc.)
  - `env.template` environment template (**do not commit real `.env`**)

- **Backend structure (`backend/app/`)**
  - `main.py` FastAPI app + routers + CORS + global error handler
  - `routers/` REST + MCP endpoints (`auth`, `buckets`, `files`, `chat`, `api_keys`, `mcp`, `mcp_server`, `oauth`)
  - `services/` supabase client, file processing, MCP auth/services, OAuth2 service, rate limiting
  - `models/` Pydantic models (buckets/files/api keys/mcp/oauth)
  - `utils/error_logger.py` error tracing + DB logging with redaction

- **Frontend structure (`frontend/src/`)**
  - `App.jsx` routing
  - `pages/` Login/Signup/ForgotPassword/Dashboard/Bucket
  - `components/` UI components including Profile Settings (API Keys + OAuth Clients)
  - `services/api.js` axios client + API helpers

---

## 3. Core Runtime (The Heart)
- **Backend entry**
  - `backend/run.py` starts Uvicorn (`app.main:app`) on `settings.backend_port` (default `7223`).
  - `backend/app/main.py` registers all routers, adds CORS, has global exception handler.

- **Frontend entry**
  - `frontend/src/main.jsx` (React entry) + `frontend/src/App.jsx` (routes)
  - Default dev ports: frontend `6677`, backend `7223`.

---

## 4. Model / AI Layer
- **AI is already wired.**
- **Primary model**: DeepSeek (via OpenAI-compatible SDK).
  - Chat prompt lives in `backend/app/routers/chat.py` (`SYSTEM_PROMPT`).
  - Calls are made with `deepseek_client.chat.completions.create(...)`.
- **File analysis / summaries**
  - `backend/app/services/file_processor.py` extracts text + chunks + generates “comprehensive analysis” via DeepSeek.
- **Embeddings**
  - `generate_embedding()` exists but is currently a placeholder returning `None`.

---

## 5. Memory / State / Knowledge
- **Persistence**: Supabase (Postgres + Storage) is the core state store.
  - Tables implied by code: `buckets`, `files`, `chunks`, `summaries`, `conversations`, `messages`, `api_keys`, plus oauth tables.
- **Knowledge format**
  - Files are stored in Supabase Storage; extracted text is stored as `chunks` (and `summaries`).
- **Vector DB**
  - Schema mentions pgvector; however embedding generation is currently stubbed, so “semantic search” is likely incomplete until embeddings are implemented end-to-end.

---

## 6. Interfaces (How humans touch it)
- **Frontend UI (primary)**
  - Auth pages + dashboard + bucket chat UI.
  - Profile Settings includes API Keys and OAuth Clients management.
- **REST API**
  - Core: `/api/auth/*`, `/api/buckets/*`, `/api/buckets/{id}/files`, `/api/buckets/{id}/chat`, `/api/api-keys/*`
- **MCP**
  - REST-style MCP endpoints under `/mcp/*` (API key auth)
  - MCP protocol + resources + OAuth endpoints under `/mcp/server/*` (for Cursor/ChatGPT style clients)
  - Stdio transport exists for Cursor via `backend/app/mcp_stdio.py`
- **Current usage**
  - Primarily you (owner/dev), with capability for real users once deployed.

---

## 7. Configuration & Secrets
- **Template available**: `env.template`
- **Backend config**: `backend/app/config.py` loads from project root `.env`

- **Deployability**
  - Deployable, but must set production secrets and tighten CORS/origins.
  - Important: never expose/return secrets in API/MCP responses.

---

## 8. Tests & Reliability (Probably painful)
- **Tests**: No first-party test suite found (outside of `node_modules` / `venv`).
- **Error handling**
  - Backend has a global exception handler (`backend/app/main.py`).
  - There is a dedicated error tracing utility with redaction + DB logging (`backend/app/utils/error_logger.py`).
- **Known reliability risks**
  - Heavy “full bucket context” can become slow/large as buckets grow (needs retrieval/limits).
  - Semantic search depends on embeddings which are currently stubbed.

---

## 9. What You *Think* Is Broken
Be honest. No judgment.

- **OAuth authorize flow**: `/mcp/server/oauth/authorize` is currently a placeholder (no real login/consent + redirect with code).
- **Security risk**: ensure MCP/resources never leak internal config/secrets (keep sanitization strict).
- **Cursor MCP stdio**: historically flaky; HTTP/SSE is typically easier once deployed.

---

## 10. What You Want *Next*
Not the dream — the **next concrete win**.

- **Deploy production**
  - Domain + HTTPS + production env + stable MCP HTTP endpoint.
- **Finish OAuth**
  - Implement a real authorize/login/consent flow that returns authorization codes and redirects correctly.
- **Harden security**
  - Strict output sanitization for MCP responses and logs; rotate secrets before launch.

---

## Status (we will fill this later)
- **Current maturity level**: Feature-complete MVP (UI + API + MCP), but integrations need finishing.
- **Biggest blocker**: Production deployment + completing OAuth authorize/consent flow.
- **Next irreversible step**: Go live on a domain (rotate secrets + lock down CORS + RLS policies verified).

---

> Keep this file updated as you ship. It’s your “truth doc.”

