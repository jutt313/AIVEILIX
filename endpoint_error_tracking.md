# Endpoint Error Tracking & Clean Error Plan

## The Problem
Most endpoints use `raise HTTPException(status_code=500, detail=str(e))` which leaks raw Python errors to users. Example of what users currently see:

> "Connection to database timed out after 30 seconds at postgres://user:password@host..."

What they should see:

> "Something went wrong. Please try again."

---

## Current Status Per Router

| Router | Endpoints | Status |
|--------|-----------|--------|
| auth.py | 8 | ❌ Raw `str(e)` |
| buckets.py | 8 | ❌ Raw `str(e)` |
| files.py | 10 | ❌ Raw `str(e)` |
| chat.py | 5 | ❌ Raw `str(e)` |
| api_keys.py | 3 | ❌ Raw `str(e)` |
| oauth.py | 3 | ❌ Raw `str(e)` on 2 |
| notifications.py | 6 | ❌ Raw `str(e)` |
| team.py | 10 | ❌ Raw `str(e)` |
| mcp.py | 6 | ✅ Already sanitized |
| mcp_server.py | 7 | ✅ Already sanitized |
| stripe.py | 6 | ✅ Already sanitized |

**Total: 63 endpoints need fixing, 19 already good**

---

## All Endpoints

### AUTH (8 endpoints)
| Method | Path | Current Error | Clean Error |
|--------|------|---------------|-------------|
| POST | /api/auth/signup | `str(e)` — could leak DB error | "Failed to create account. Please try again." |
| POST | /api/auth/login | `str(e)` — could leak auth details | "Login failed. Please check your credentials." |
| POST | /api/auth/forgot-password | `str(e)` | "Failed to send reset email. Please try again." |
| POST | /api/auth/reset-password | `str(e)` | "Failed to reset password. The link may have expired." |
| POST | /api/auth/logout | `str(e)` | "Logout failed. Please try again." |
| GET | /api/auth/me | `str(e)` | "Failed to load user info. Please log in again." |
| POST | /api/auth/change-password | `str(e)` | "Failed to change password. Please try again." |
| POST | /api/auth/delete-account | `str(e)` | "Failed to delete account. Please try again." |

### BUCKETS (8 endpoints)
| Method | Path | Current Error | Clean Error |
|--------|------|---------------|-------------|
| GET | /api/buckets | `str(e)` | "Failed to load buckets. Please try again." |
| POST | /api/buckets | `str(e)` | "Failed to create bucket. Please try again." |
| GET | /api/buckets/{id} | `str(e)` | "Failed to load bucket. Please try again." |
| DELETE | /api/buckets/{id} | `str(e)` | "Failed to delete bucket. Please try again." |
| POST | /api/buckets/delete-all | `str(e)` | "Failed to delete buckets. Please try again." |
| GET | /api/buckets/stats/dashboard | `str(e)` | "Failed to load stats. Please try again." |
| GET | /api/buckets/stats/activity | `str(e)` | "Failed to load activity. Please try again." |

### FILES (10 endpoints)
| Method | Path | Current Error | Clean Error |
|--------|------|---------------|-------------|
| POST | /api/buckets/{id}/upload | `str(e)` — could leak storage URL/path | "Failed to upload file. Please try again." |
| POST | /api/buckets/{id}/register-upload | `str(e)` | "Failed to register upload. Please try again." |
| POST | /api/buckets/{id}/files/create | `str(e)` | "Failed to create file. Please try again." |
| PUT | /api/buckets/{id}/files/{fid}/content | `str(e)` | "Failed to update file content. Please try again." |
| GET | /api/buckets/{id}/files | `str(e)` | "Failed to load files. Please try again." |
| GET | /api/buckets/{id}/files/{fid}/content | `str(e)` | "Failed to load file. Please try again." |
| PUT | /api/buckets/{id}/files/{fid}/summary | `str(e)` | "Failed to update summary. Please try again." |
| GET | /api/buckets/{id}/search | `str(e)` | "Search failed. Please try again." |
| GET | /api/buckets/{id}/semantic-search | `str(e)` — could leak embedding errors | "Search failed. Please try again." |
| DELETE | /api/buckets/{id}/files/{fid} | `str(e)` | "Failed to delete file. Please try again." |

### CHAT (5 endpoints)
| Method | Path | Current Error | Clean Error |
|--------|------|---------------|-------------|
| POST | /api/buckets/{id}/chat | `str(e)` — could leak AI API keys/responses | "Failed to send message. Please try again." |
| GET | /api/buckets/{id}/conversations | `str(e)` | "Failed to load conversations. Please try again." |
| GET | /api/conversations/{id}/messages | `str(e)` | "Failed to load messages. Please try again." |
| PATCH | /api/conversations/{id} | `str(e)` | "Failed to update conversation. Please try again." |
| DELETE | /api/conversations/{id} | `str(e)` | "Failed to delete conversation. Please try again." |

### API KEYS (3 endpoints)
| Method | Path | Current Error | Clean Error |
|--------|------|---------------|-------------|
| POST | /api/api-keys | `str(e)` | "Failed to create API key. Please try again." |
| GET | /api/api-keys | `str(e)` | "Failed to load API keys. Please try again." |
| DELETE | /api/api-keys/{id} | `str(e)` | "Failed to revoke API key. Please try again." |

### NOTIFICATIONS (6 endpoints)
| Method | Path | Current Error | Clean Error |
|--------|------|---------------|-------------|
| GET | /api/notifications | `str(e)` | "Failed to load notifications. Please try again." |
| GET | /api/notifications/unread-count | `str(e)` | "Failed to get notification count." |
| POST | /api/notifications | `str(e)` | "Failed to create notification." |
| PATCH | /api/notifications/{id}/read | `str(e)` | "Failed to mark as read." |
| PATCH | /api/notifications/mark-all-read | `str(e)` | "Failed to mark all as read." |
| DELETE | /api/notifications/{id} | `str(e)` | "Failed to delete notification." |

### OAUTH (3 endpoints)
| Method | Path | Current Error | Clean Error |
|--------|------|---------------|-------------|
| GET | /api/oauth/authorize | HTTPException only (ok) | — |
| POST | /api/oauth/token | `str(e)` | "Token exchange failed. Please try again." |
| POST | /api/oauth/clients | `str(e)` | "Failed to register client. Please try again." |

### TEAM (10 endpoints)
| Method | Path | Current Error | Clean Error |
|--------|------|---------------|-------------|
| POST | /api/team/members | `str(e)` | "Failed to add member. Please try again." |
| GET | /api/team/members | `str(e)` | "Failed to load team members. Please try again." |
| GET | /api/team/members/{id} | `str(e)` | "Failed to load member. Please try again." |
| PATCH | /api/team/members/{id} | `str(e)` | "Failed to update member. Please try again." |
| DELETE | /api/team/members/{id} | `str(e)` | "Failed to remove member. Please try again." |
| POST | /api/team/members/{id}/buckets | `str(e)` | "Failed to assign bucket. Please try again." |
| GET | /api/team/members/{id}/buckets | `str(e)` | "Failed to load member buckets. Please try again." |
| DELETE | /api/team/members/{id}/buckets/{bid} | `str(e)` | "Failed to unassign bucket. Please try again." |
| GET | /api/team/activity | `str(e)` | "Failed to load activity. Please try again." |
| GET | /api/team/me | HTTPException only (ok) | — |

### MCP (6 endpoints) — ✅ ALREADY GOOD
| Method | Path | Status |
|--------|------|--------|
| GET | /mcp/buckets | ✅ sanitize_error_message() |
| GET | /mcp/buckets/{id}/files | ✅ sanitize_error_message() |
| POST | /mcp/buckets/{id}/query | ✅ sanitize_error_message() |
| POST | /mcp/buckets/{id}/chat | ✅ sanitize_error_message() |
| GET | /mcp/buckets/{id}/files/{fid}/content | ✅ sanitize_error_message() |

### STRIPE (6 endpoints) — ✅ ALREADY GOOD
| Method | Path | Status |
|--------|------|--------|
| POST | /api/stripe/checkout | ✅ get_stripe_error_detail() |
| POST | /api/stripe/webhook | ✅ sanitized |
| GET | /api/stripe/portal | ✅ get_stripe_error_detail() |
| GET | /api/stripe/subscription | ✅ sanitized |
| POST | /api/stripe/cancel | ✅ get_stripe_error_detail() |
| POST | /api/stripe/reactivate | ✅ get_stripe_error_detail() |

---

## Implementation Plan

### Step 1 — Create a shared error utility (backend)
**File:** `backend/app/utils/errors.py`

Add one function used by all routers:
```python
def safe_error(msg: str, exc: Exception, status: int = 500):
    logger.error(f"{msg}: {exc}")
    raise HTTPException(status_code=status, detail=msg)
```

Instead of:
```python
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

Use:
```python
except Exception as e:
    safe_error("Failed to load buckets. Please try again.", e)
```

---

### Step 2 — Fix auth.py (8 endpoints)
Replace all `detail=str(e)` with specific clean messages per endpoint.
Log the real error internally. Never expose it.

---

### Step 3 — Fix buckets.py (8 endpoints)
Same pattern. Each endpoint gets its own clean message.

---

### Step 4 — Fix files.py (10 endpoints)
Most important. File upload errors currently expose storage paths. Fix all 10.

---

### Step 5 — Fix chat.py (5 endpoints)
Chat errors can expose AI API key names or model errors. Fix all 5.

---

### Step 6 — Fix api_keys.py (3 endpoints)
Short and simple. Fix all 3.

---

### Step 7 — Fix notifications.py (6 endpoints)
Low priority (internal only), but fix for consistency.

---

### Step 8 — Fix oauth.py (2 endpoints)
Fix `/token` and `/clients` only. `/authorize` uses HTTPException which is fine.

---

### Step 9 — Fix team.py (10 endpoints)
Fix all 10. These can leak member data / permission errors.

---

### Step 10 — Add a global toast system to frontend
**File:** `frontend/src/components/Toast.jsx` (new)

One simple toast component that shows errors from API responses. Instead of `alert()` or silent failures scattered across the app, all API errors go to one toast.

Show:
- The clean message from the backend (e.g. "Failed to upload file. Please try again.")
- Red background, auto-dismiss after 5 seconds
- "X" to close early

---

### Step 11 — Update frontend API service to use toast
**File:** `frontend/src/services/api.js`

In the Axios response interceptor, catch all errors and show them in the toast:
```javascript
// Instead of per-component error handling, one global handler:
error.response?.data?.detail || "Something went wrong. Please try again."
```

---

### Step 12 — Remove scattered `alert()` calls from frontend
Search all components for `alert(` and replace with the toast system.

---

## Priority Order

1. **Step 1** — Create `utils/errors.py` utility (5 min, unlocks all others)
2. **Step 2** — auth.py (high priority — auth errors are sensitive)
3. **Step 4** — files.py (high priority — storage paths leak here)
4. **Step 3** — buckets.py
5. **Step 5** — chat.py (AI API errors can be verbose)
6. **Step 10+11** — Frontend toast system (user-facing improvement)
7. **Step 6** — api_keys.py
8. **Step 8** — oauth.py
9. **Step 9** — team.py
10. **Step 7** — notifications.py (lowest risk, internal)

---

## What "Done" Looks Like

- No `str(e)` in any HTTP response
- Every endpoint logs the real error internally
- User sees a short, friendly message
- Frontend shows it in a clean toast (not `alert()`)
- No stack traces, no DB urls, no API key names ever reach the browser
