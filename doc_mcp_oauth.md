# AIveilix MCP OAuth Integration — Fix Documentation

## Problem
OAuth2 flow was failing when connecting AIveilix to ChatGPT and Claude.
Both showed generic errors ("something went wrong" / "Invalid redirect_uri") with no useful debug info.

---

## Root Causes Found (4 Blockers + 3 Security Issues)

### Blocker 1: DCR Endpoint Required Auth
- **File**: `backend/app/routers/mcp_server.py` → `/mcp/server/oauth/register`
- **Problem**: `Depends(get_mcp_user)` required an API key before registration. ChatGPT/Claude call DCR before any auth exists.
- **Fix**: Removed auth dependency. New `create_client_public()` method creates clients with `user_id=None`.

### Blocker 2: No Login/Consent Page
- **File**: `backend/app/routers/mcp_server.py` → `/mcp/server/oauth/authorize`
- **Problem**: Endpoint auto-approved using `client["user_id"]` and instantly redirected with a code. No user interaction at all.
- **Fix**: Now redirects to React frontend `/oauth/authorize` for login + consent. New `/mcp/server/oauth/approve` endpoint handles the callback after user approves.

### Blocker 3: client_secret Required for PKCE Clients
- **File**: `backend/app/routers/mcp_server.py` → `/mcp/server/oauth/token`
- **Problem**: `client_secret: str = Form(...)` was required. PKCE public clients (ChatGPT/Claude) don't send a client_secret.
- **Fix**: Made `client_secret` optional. If missing, `code_verifier` is required (PKCE). Added `refresh_tokens_public()` for public client refresh.

### Blocker 4: Discovery Missing "none" Auth Method
- **File**: `backend/app/main.py` → `/.well-known/oauth-authorization-server`
- **Problem**: Only advertised `client_secret_basic` and `client_secret_post`. PKCE public clients need `none`.
- **Fix**: Added `"none"` to `token_endpoint_auth_methods_supported`.

### Security P1: Redirect URI Not Validated on Approve
- **File**: `backend/app/routers/mcp_server.py` → `/mcp/server/oauth/approve`
- **Problem**: The approve endpoint accepted any `redirect_uri` from the form POST without checking it against the client's registered URI or the allowlist.
- **Fix**: Added validation: `redirect_uri` must match `client["redirect_uri"]` OR be in `ALLOWED_REDIRECT_URIS`.

### Security P1: Scopes Not Enforced Against Client Scopes
- **File**: `backend/app/routers/mcp_server.py` → `/mcp/server/oauth/approve`
- **Problem**: Any scope string from the form was written into the auth code without checking it's a subset of the client's registered scopes.
- **Fix**: Added scope subset validation. Rejects with 400 if requested scopes exceed client's registered scopes.

### Security P2: Frontend Redirect Without Guard
- **File**: `backend/app/routers/mcp_server.py` → `/mcp/server/oauth/authorize`
- **Problem**: `settings.frontend_url` used without null check. If unset, redirect goes to `None/oauth/authorize`.
- **Fix**: Added guard that returns 500 with clear error if `frontend_url` is empty.

---

## Files Changed

### Backend
| File | Change |
|------|--------|
| `backend/app/routers/mcp_server.py` | DCR public, authorize→React redirect, /approve endpoint, token optional secret, redirect_uri validation, scope enforcement, frontend_url guard, ALLOWED_REDIRECT_URIS |
| `backend/app/services/oauth2.py` | Added `create_client_public()`, `refresh_tokens_public()` |
| `backend/app/main.py` | Added `"none"` to token_endpoint_auth_methods_supported |

### Frontend
| File | Change |
|------|--------|
| `frontend/src/pages/OAuthAuthorize.jsx` | New page — login form + consent screen for OAuth flow |
| `frontend/src/App.jsx` | Added route `/oauth/authorize` → `OAuthAuthorize` |

### Database
| File | Change |
|------|--------|
| `supabase/migrations/010_oauth_public_clients.sql` | Makes `user_id` nullable on `oauth_clients` for public DCR |

---

## Database Migration Required

Run this on Supabase before deploying:

```sql
ALTER TABLE oauth_clients ALTER COLUMN user_id DROP NOT NULL;
```

---

## Allowed Redirect URIs

The backend maintains an allowlist in `mcp_server.py`:

```python
ALLOWED_REDIRECT_URIS = [
    "https://chatgpt.com/connector_platform_oauth_redirect",
    "https://platform.openai.com/apps-manage/oauth",
    "https://claude.ai/oauth/callback",
    "http://localhost:6677/oauth/callback",
    "http://localhost:7223/oauth/callback",
    "http://127.0.0.1:6677/oauth/callback",
    "http://127.0.0.1:7223/oauth/callback",
]
```

---

## Claude Connector Config

In Claude Settings → Connectors → Add custom connector:

| Field | Value |
|-------|-------|
| Name | aiveilix |
| URL | `https://api.aiveilix.com/mcp/server/protocol/sse` |
| Client ID | `mcp_MFcreGH3PHIF-y6wkw8sYbBX1i4wFb8M` |
| Client Secret | (the secret from when client was created) |

Claude automatically uses `https://claude.ai/oauth/callback` as the redirect_uri.

**Important**: The OAuth client in the DB must either:
- Have `redirect_uri = 'https://claude.ai/oauth/callback'` registered, OR
- The allowlist covers it (which it now does)

To update the client's registered redirect_uri:
```sql
UPDATE oauth_clients
SET redirect_uri = 'https://claude.ai/oauth/callback'
WHERE client_id = 'mcp_MFcreGH3PHIF-y6wkw8sYbBX1i4wFb8M';
```

---

## OAuth Flow After Fix

```
Claude/ChatGPT                    Backend                         React Frontend
     |                               |                                  |
     |-- GET /.well-known/oauth -->  |                                  |
     |<-- discovery metadata --------|                                  |
     |                               |                                  |
     |-- POST /oauth/register ------>|  (public, no auth needed)        |
     |<-- client_id + secret --------|                                  |
     |                               |                                  |
     |-- GET /oauth/authorize ------>|                                  |
     |                               |-- 302 redirect ---------------->|
     |                               |                                  |
     |                               |            user sees login form  |
     |                               |            user logs in          |
     |                               |            user sees consent     |
     |                               |            user clicks Authorize |
     |                               |                                  |
     |                               |<-- POST /oauth/approve ---------|
     |                               |    (with JWT + oauth params)     |
     |                               |                                  |
     |<-- 302 redirect + code -------|                                  |
     |                               |                                  |
     |-- POST /oauth/token --------->|  (code + code_verifier, no secret)
     |<-- access_token + refresh ----|                                  |
     |                               |                                  |
     |-- POST /mcp/server/protocol ->|  (Bearer access_token)          |
     |<-- tool results --------------|                                  |
```

---

## Deployment Checklist

1. [ ] Run DB migration: `ALTER TABLE oauth_clients ALTER COLUMN user_id DROP NOT NULL;`
2. [ ] Deploy updated backend code
3. [ ] Deploy updated frontend code (new OAuthAuthorize page)
4. [ ] Verify `BACKEND_URL` and `FRONTEND_URL` env vars are set correctly in production
5. [ ] Verify `https://api.aiveilix.com` CORS allows `https://claude.ai` origin (if needed)
6. [ ] Update OAuth client redirect_uri in DB if needed
7. [ ] Test: Add connector in Claude → should see login page → authorize → connected
