# AIveilix API — Production Readiness Report

**Generated:** 2026-02-28 23:50:24  
**Base URL:** `https://api.aiveilix.com`  

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 20 |
| Passed | 15 (75.0%) |
| Failed | 5 |
| Skipped | 2 |

### Verdict: 🔴 **NOT PRODUCTION READY**

> Critical endpoint failures detected. Fix before deploying.

---

## Group Results

| Group | Passed | Failed | Status |
|-------|--------|--------|--------|
| Health | 2 | 0 | ✅ |
| Auth | 3 | 4 | ❌ |
| MCP | 4 | 0 | ✅ |
| Security | 5 | 1 | ❌ |
| Cleanup | 1 | 0 | ✅ |

---

## Detailed Results


### Health

| Status | Endpoint | HTTP | Duration | Notes |
|--------|----------|------|----------|-------|
| ✅ | `GET / — root` | 200 | 467.9ms |  |
| ✅ | `GET /health` | 200 | 415.5ms |  |

### Auth

| Status | Endpoint | HTTP | Duration | Notes |
|--------|----------|------|----------|-------|
| ❌ | `POST /api/auth/signup` | 0 | 4029.9ms |  |
| ❌ | `POST /api/auth/login` | 0 | 1289.3ms |  |
| ❌ | `GET /api/auth/me` | 0 | 315.1ms |  |
| ❌ | `POST /api/auth/forgot-password` | 0 | 390.3ms |  |
| ✅ | `POST /api/auth/logout` | 200 | 322.1ms |  |
| ✅ | `POST /api/auth/change-password (wrong pass → 401)` | 0 | 370.6ms |  |
| ✅ | `POST /api/auth/delete-account` | 0 | 0ms | SKIPPED (SKIP_DESTRUCTIVE=1) |

### MCP

| Status | Endpoint | HTTP | Duration | Notes |
|--------|----------|------|----------|-------|
| ✅ | `GET /.well-known/oauth-authorization-server` | 200 | 349.4ms |  |
| ✅ | `GET /.well-known/oauth-protected-resource` | 200 | 336.6ms |  |
| ✅ | `GET /.well-known/openid-configuration` | 200 | 319.7ms |  |
| ✅ | `MCP endpoints (require API key)` | 0 | 0ms | SKIPPED — no token |

### Security

| Status | Endpoint | HTTP | Duration | Notes |
|--------|----------|------|----------|-------|
| ✅ | `GET /api/buckets/ without auth → 401` | 0 | 347.1ms |  |
| ✅ | `GET /api/api-keys/ without auth → 401` | 0 | 324.0ms |  |
| ✅ | `GET /api/notifications without auth → 401` | 0 | 322.3ms |  |
| ✅ | `GET /api/auth/me without auth → 401` | 0 | 371.0ms |  |
| ✅ | `GET /api/auth/me with invalid token → 401` | 0 | 1121.8ms |  |
| ❌ | `GET /api/buckets/{random_uuid} → 404/500` | 0 | 373.7ms | app bug: returns 500 instead of 404 |

### Cleanup

| Status | Endpoint | HTTP | Duration | Notes |
|--------|----------|------|----------|-------|
| ✅ | `DELETE /api/buckets/{test_bucket}` | 0 | 0ms | Nothing to clean |

---

## ❌ Failures

- **[Auth]** `POST /api/auth/signup` — HTTP 0
- **[Auth]** `POST /api/auth/login` — HTTP 0
- **[Auth]** `GET /api/auth/me` — HTTP 0
- **[Auth]** `POST /api/auth/forgot-password` — HTTP 0
- **[Security]** `GET /api/buckets/{random_uuid} → 404/500` — HTTP 0 — app bug: returns 500 instead of 404

---

## Production Checklist

- [☐] 🔐 Auth endpoints (signup, login, me, logout)
- [☐] 🗂️ Bucket CRUD and stats
- [☐] 📁 File upload, processing, search
- [☐] 💬 AI chat with streaming SSE
- [☐] 🔑 API key generation and validation
- [☐] 🔔 Notification system
- [☐] 👥 Team management
- [☐] 💳 Stripe billing integration
- [☑] 🔌 MCP protocol endpoints
- [☐] 🔒 Security / auth enforcement

---

## Environment

- Backend URL: `https://api.aiveilix.com`
- Test account: `your@email.com`
- Skip destructive: `True`
- Skip chat: `False`
- Skip Stripe: `True`
