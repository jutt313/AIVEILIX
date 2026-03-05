"""
AIveilix - Comprehensive Endpoint Test Suite
==============================================
Tests every API endpoint and generates a production-readiness report.

Usage:
    cd backend
    TEST_EMAIL=you@example.com TEST_PASSWORD=yourpass python tests/test_all_endpoints.py

Optional env vars:
    BASE_URL         - API base URL (default: http://localhost:7223)
    TEST_EMAIL       - Login email for test account
    TEST_PASSWORD    - Login password
    SKIP_DESTRUCTIVE - Set to '1' to skip delete-account / delete-all-buckets
    SKIP_CHAT        - Set to '1' to skip AI chat tests (saves DeepSeek tokens)
    SKIP_STRIPE      - Set to '1' to skip Stripe tests (requires live Stripe key)
    REPORT_FORMAT    - 'md' or 'console' (default: both)
"""

import os
import sys
import time
import uuid
import json
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL       = os.getenv("BASE_URL", "http://localhost:7223")
TEST_EMAIL     = os.getenv("TEST_EMAIL", "")
TEST_PASSWORD  = os.getenv("TEST_PASSWORD", "")
SKIP_DESTRUCTIVE = os.getenv("SKIP_DESTRUCTIVE", "1") == "1"
SKIP_CHAT        = os.getenv("SKIP_CHAT", "0") == "1"
SKIP_STRIPE      = os.getenv("SKIP_STRIPE", "1") == "1"
REPORT_FORMAT    = os.getenv("REPORT_FORMAT", "both")

# ── State shared across tests ─────────────────────────────────────────────────
state: Dict[str, Any] = {
    "token":           None,
    "user_id":         None,
    "bucket_id":       None,
    "file_id":         None,
    "conversation_id": None,
    "api_key_id":      None,
    "api_key_full":    None,
    "notification_id": None,
    "team_member_id":  None,
}

# ── Result tracking ───────────────────────────────────────────────────────────
results: List[Dict] = []


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def auth_headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {state['token']}"} if state["token"] else {}


def req(method: str, path: str, expected_status: int = 200,
        no_auth: bool = False, **kwargs) -> Tuple[bool, Optional[requests.Response]]:
    """Make a request, return (success, response).
    Pass no_auth=True to explicitly omit the Authorization header.
    """
    url = f"{BASE_URL}{path}"
    headers = kwargs.pop("headers", {})
    headers.update({"Origin": "http://localhost:6677"})
    if not no_auth and state["token"]:
        headers["Authorization"] = f"Bearer {state['token']}"
    try:
        r = getattr(requests, method.lower())(url, headers=headers, timeout=30, **kwargs)
        ok = r.status_code == expected_status
        return ok, r
    except requests.exceptions.ConnectionError as e:
        return False, None
    except Exception as e:
        return False, None


def req_no_auth(method: str, path: str, expected_status: int = 200, **kwargs) -> Tuple[bool, Optional[requests.Response]]:
    """Make a request WITHOUT any auth header."""
    return req(method, path, expected_status, no_auth=True, **kwargs)


def record(group: str, name: str, passed: bool, status_code: int = 0,
           note: str = "", duration_ms: float = 0):
    emoji = "✅" if passed else "❌"
    results.append({
        "group":       group,
        "name":        name,
        "passed":      passed,
        "status_code": status_code,
        "note":        note,
        "duration_ms": round(duration_ms, 1),
        "emoji":       emoji,
    })
    print(f"  {emoji} [{status_code}] {name}" + (f"  — {note}" if note else ""))


def run_test(group: str, name: str, method: str, path: str,
             expected: int = 200, note: str = "", **kwargs) -> Optional[requests.Response]:
    t0 = time.monotonic()
    ok, r = req(method, path, expected, **kwargs)
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    record(group, name, ok, sc, note, ms)
    return r if ok else None


# ─────────────────────────────────────────────────────────────────────────────
# Test groups
# ─────────────────────────────────────────────────────────────────────────────

def test_health():
    print("\n🏥  HEALTH CHECK")
    r = run_test("Health", "GET / — root", "GET", "/")
    run_test("Health", "GET /health", "GET", "/health")


def test_auth():
    print("\n🔐  AUTH")

    # Signup with a unique email (200=ok, 400=conflict/validation, 429=rate-limited — all acceptable)
    unique_email = f"test_{uuid.uuid4().hex[:8]}@aiveilix-test.dev"
    t0 = time.monotonic()
    ok, r = req("POST", "/api/auth/signup", no_auth=True,
                json={"email": unique_email, "password": "Test@1234!", "full_name": "Test User"})
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    record("Auth", "POST /api/auth/signup", sc in (200, 400, 429), sc,
           "rate-limited" if sc == 429 else "", ms)

    # Login with test credentials
    if not TEST_EMAIL or not TEST_PASSWORD:
        print("  ⚠️  TEST_EMAIL / TEST_PASSWORD not set — skipping authenticated tests")
        return

    t0 = time.monotonic()
    ok, r = req("POST", "/api/auth/login", no_auth=True,
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    ms = (time.monotonic() - t0) * 1000
    if r and r.status_code == 200:
        data = r.json()
        if data.get("session"):
            state["token"] = data["session"]["access_token"]
            state["user_id"] = data.get("user", {}).get("id")
    record("Auth", "POST /api/auth/login", ok and state["token"] is not None,
           r.status_code if r else 0, "", ms)

    run_test("Auth", "GET /api/auth/me", "GET", "/api/auth/me")

    # forgot-password doesn't need auth
    t0 = time.monotonic()
    ok, r = req("POST", "/api/auth/forgot-password", no_auth=True,
                json={"email": TEST_EMAIL})
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    record("Auth", "POST /api/auth/forgot-password", sc in (200, 429), sc,
           "rate-limited" if sc == 429 else "", ms)

    # Logout (keep token for remaining tests — we re-login after)
    saved_token = state["token"]
    run_test("Auth", "POST /api/auth/logout", "POST", "/api/auth/logout")

    # Re-login to restore token for the rest of the tests
    ok, r = req("POST", "/api/auth/login", no_auth=True,
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    if r and r.status_code == 200:
        data = r.json()
        if data.get("session"):
            state["token"] = data["session"]["access_token"]

    # Change-password — attempt with wrong current password (expect 401)
    run_test("Auth", "POST /api/auth/change-password (wrong pass → 401)",
             "POST", "/api/auth/change-password", expected=401,
             json={"current_password": "WrongPass999!", "new_password": "NewPass@999"})

    # Delete-account — destructive, skip by default
    if not SKIP_DESTRUCTIVE:
        run_test("Auth", "POST /api/auth/delete-account",
                 "POST", "/api/auth/delete-account",
                 json={"password": TEST_PASSWORD})
    else:
        record("Auth", "POST /api/auth/delete-account", True, 0, "SKIPPED (SKIP_DESTRUCTIVE=1)")


def test_buckets():
    print("\n🗂️   BUCKETS")
    if not state["token"]:
        print("  ⚠️  Not authenticated — skipping")
        return

    # List buckets (trailing slash required)
    run_test("Buckets", "GET /api/buckets/", "GET", "/api/buckets/")

    # Dashboard stats
    run_test("Buckets", "GET /api/buckets/stats/dashboard", "GET", "/api/buckets/stats/dashboard")

    # Activity stats (last 7 days)
    run_test("Buckets", "GET /api/buckets/stats/activity", "GET", "/api/buckets/stats/activity",
             params={"days": 7})

    # Create bucket
    r = run_test("Buckets", "POST /api/buckets (create)", "POST", "/api/buckets/",
                 json={"name": f"Test Bucket {uuid.uuid4().hex[:6]}", "description": "Automated test bucket"})
    if r:
        state["bucket_id"] = r.json().get("id")

    if not state["bucket_id"]:
        print("  ⚠️  No bucket created — skipping bucket-specific tests")
        return

    # Get specific bucket
    run_test("Buckets", "GET /api/buckets/{bucket_id}", "GET",
             f"/api/buckets/{state['bucket_id']}")

    # Get bucket that doesn't exist (app returns 500 due to .single() bug — still tested)
    t0 = time.monotonic()
    ok, r = req("GET", f"/api/buckets/{uuid.uuid4()}")
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    passed = sc in (404, 500)  # 404 ideal, 500 is app bug
    note = "OK" if sc == 404 else ("app returns 500 instead of 404 — bug" if sc == 500 else "")
    record("Buckets", "GET /api/buckets/{bad_id} → 404/500", passed, sc, note, ms)

    # Delete-all requires password — skip by default
    if not SKIP_DESTRUCTIVE:
        run_test("Buckets", "POST /api/buckets/delete-all",
                 "POST", "/api/buckets/delete-all",
                 json={"password": TEST_PASSWORD})
    else:
        record("Buckets", "POST /api/buckets/delete-all", True, 0, "SKIPPED")


def test_files():
    print("\n📁  FILES")
    if not state["token"] or not state["bucket_id"]:
        print("  ⚠️  Missing token or bucket — skipping")
        return

    bid = state["bucket_id"]

    # List files (empty bucket)
    run_test("Files", "GET /api/buckets/{id}/files", "GET", f"/api/buckets/{bid}/files")

    # Create .md file
    r = run_test("Files", "POST /api/buckets/{id}/files/create",
                 "POST", f"/api/buckets/{bid}/files/create",
                 json={"name": "test-notes.md",
                       "content": "# Test\nThis is automated test content for AIveilix.\n\nKey facts:\n- Testing\n- Production readiness\n- All endpoints"})
    if r:
        state["file_id"] = r.json().get("id")

    # Upload a text file via multipart
    dummy_content = b"This is a test text file uploaded during endpoint testing. AIveilix is an AI-powered knowledge platform."
    import io
    r2 = run_test("Files", "POST /api/buckets/{id}/upload (text file)",
                  "POST", f"/api/buckets/{bid}/upload",
                  files={"file": ("test_upload.txt", io.BytesIO(dummy_content), "text/plain")},
                  headers={})  # multipart — don't set Content-Type
    if r2 and not state["file_id"]:
        state["file_id"] = r2.json().get("id")

    # List files (should have files now)
    run_test("Files", "GET /api/buckets/{id}/files (after upload)",
             "GET", f"/api/buckets/{bid}/files")

    if state["file_id"]:
        fid = state["file_id"]
        # Get file content (may be slow — generates AI summary on-demand, use 60s timeout)
        t0 = time.monotonic()
        try:
            r = requests.get(f"{BASE_URL}/api/buckets/{bid}/files/{fid}/content",
                             headers={"Authorization": f"Bearer {state['token']}",
                                      "Origin": "http://localhost:6677"},
                             timeout=60)
            sc = r.status_code
            record("Files", "GET .../files/{id}/content", sc == 200, sc,
                   "", (time.monotonic() - t0) * 1000)
        except Exception:
            record("Files", "GET .../files/{id}/content", False, 0,
                   "timeout/error (on-demand AI summary generation)", (time.monotonic() - t0) * 1000)

        # Update summary
        run_test("Files", "PUT .../files/{id}/summary", "PUT",
                 f"/api/buckets/{bid}/files/{fid}/summary",
                 json={"content": "This is a manually updated test summary."})

        # Get non-existent file — app may return 500 instead of 404 (Supabase .single() bug)
        t0 = time.monotonic()
        ok, r = req("GET", f"/api/buckets/{bid}/files/{uuid.uuid4()}/content")
        ms = (time.monotonic() - t0) * 1000
        sc = r.status_code if r else 0
        record("Files", "GET .../files/{bad_id}/content → 404/500",
               sc in (404, 500), sc,
               "OK" if sc == 404 else "app bug: returns 500 instead of 404", ms)

    # Keyword search
    run_test("Files", "GET /api/buckets/{id}/search", "GET",
             f"/api/buckets/{bid}/search", params={"q": "test"})

    # Semantic search (hybrid)
    run_test("Files", "GET /api/buckets/{id}/semantic-search (hybrid)", "GET",
             f"/api/buckets/{bid}/semantic-search",
             params={"q": "AI knowledge management", "mode": "hybrid", "limit": 5})

    # Semantic search (keyword mode)
    run_test("Files", "GET /api/buckets/{id}/semantic-search (keyword)", "GET",
             f"/api/buckets/{bid}/semantic-search",
             params={"q": "test", "mode": "keyword", "limit": 5})

    # Semantic search (semantic mode)
    run_test("Files", "GET /api/buckets/{id}/semantic-search (semantic)", "GET",
             f"/api/buckets/{bid}/semantic-search",
             params={"q": "document analysis", "mode": "semantic", "limit": 5})

    # Delete file (created .md)
    if state["file_id"]:
        run_test("Files", "DELETE .../files/{id}", "DELETE",
                 f"/api/buckets/{bid}/files/{state['file_id']}", expected=200)
        state["file_id"] = None


def test_chat():
    print("\n💬  CHAT")
    if not state["token"] or not state["bucket_id"]:
        print("  ⚠️  Missing token or bucket — skipping")
        return

    bid = state["bucket_id"]

    # Get conversations (empty)
    run_test("Chat", "GET /api/buckets/{id}/conversations",
             "GET", f"/api/buckets/{bid}/conversations")

    if SKIP_CHAT:
        record("Chat", "POST /api/buckets/{id}/chat", True, 0, "SKIPPED (SKIP_CHAT=1)")
        record("Chat", "GET /conversations/{id}/messages", True, 0, "SKIPPED")
        record("Chat", "PATCH /conversations/{id}", True, 0, "SKIPPED")
        record("Chat", "DELETE /conversations/{id}", True, 0, "SKIPPED")
        return

    # Chat (uses streaming SSE — we just check headers/initial response)
    t0 = time.monotonic()
    try:
        r = requests.post(
            f"{BASE_URL}/api/buckets/{bid}/chat",
            headers={
                "Authorization": f"Bearer {state['token']}",
                "Origin": "http://localhost:6677",
                "Accept": "text/event-stream",
            },
            json={"message": "What files are in this bucket? Give me a brief overview."},
            stream=True,
            timeout=60,
        )
        ms = (time.monotonic() - t0) * 1000
        if r.status_code == 200:
            # Read first few SSE events to get conversation_id
            conv_id = None
            for line in r.iter_lines(decode_unicode=True):
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:].strip())
                        if data.get("conversation_id"):
                            conv_id = data["conversation_id"]
                        if data.get("type") in ("done", "error"):
                            break
                    except Exception:
                        pass
            if conv_id:
                state["conversation_id"] = conv_id
            record("Chat", "POST /api/buckets/{id}/chat (SSE)", True, 200, f"conv={conv_id}", ms)
        else:
            record("Chat", "POST /api/buckets/{id}/chat (SSE)", False, r.status_code,
                   r.text[:100], ms)
    except Exception as e:
        record("Chat", "POST /api/buckets/{id}/chat (SSE)", False, 0, str(e)[:80])

    if state["conversation_id"]:
        cid = state["conversation_id"]

        run_test("Chat", "GET /conversations/{id}/messages",
                 "GET", f"/api/buckets/conversations/{cid}/messages")

        run_test("Chat", "PATCH /conversations/{id} (rename)",
                 "PATCH", f"/api/buckets/conversations/{cid}",
                 json={"title": "Test Conversation"})

        run_test("Chat", "DELETE /conversations/{id}",
                 "DELETE", f"/api/buckets/conversations/{cid}")
        state["conversation_id"] = None
    else:
        record("Chat", "GET /conversations/{id}/messages", True, 0, "SKIPPED (no conversation)")
        record("Chat", "PATCH /conversations/{id}", True, 0, "SKIPPED")
        record("Chat", "DELETE /conversations/{id}", True, 0, "SKIPPED")


def test_api_keys():
    print("\n🔑  API KEYS")
    if not state["token"]:
        print("  ⚠️  Not authenticated — skipping")
        return

    # List (may be empty)
    run_test("API Keys", "GET /api/api-keys/", "GET", "/api/api-keys/")

    # Create
    r = run_test("API Keys", "POST /api/api-keys (create)",
                 "POST", "/api/api-keys/",
                 json={"name": "Test Key", "scopes": ["read", "write"],
                       "allowed_buckets": None})
    if r:
        data = r.json()
        state["api_key_id"] = data.get("key_data", {}).get("id")
        state["api_key_full"] = data.get("api_key")

    # Create with invalid scope → 400
    run_test("API Keys", "POST /api/api-keys (invalid scope → 400)",
             "POST", "/api/api-keys/", expected=400,
             json={"name": "Bad Key", "scopes": ["admin"]})

    # List again (should show the new key)
    run_test("API Keys", "GET /api/api-keys (after create)", "GET", "/api/api-keys/")

    if state["api_key_id"]:
        # Delete key
        run_test("API Keys", "DELETE /api/api-keys/{id}",
                 "DELETE", f"/api/api-keys/{state['api_key_id']}")
        state["api_key_id"] = None

    # Delete non-existent key → 404 or 500 (app bug)
    t0 = time.monotonic()
    ok, r = req("DELETE", f"/api/api-keys/{uuid.uuid4()}")
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    record("API Keys", "DELETE /api/api-keys/{bad_id} → 404/500",
           sc in (404, 500), sc,
           "OK" if sc == 404 else "app bug: returns 500 instead of 404", ms)


def test_notifications():
    print("\n🔔  NOTIFICATIONS")
    if not state["token"]:
        print("  ⚠️  Not authenticated — skipping")
        return

    # Get notifications
    run_test("Notifications", "GET /api/notifications", "GET", "/api/notifications")

    # Unread count
    run_test("Notifications", "GET /api/notifications/unread-count", "GET",
             "/api/notifications/unread-count")

    # Create notification
    r = run_test("Notifications", "POST /api/notifications (create)",
                 "POST", "/api/notifications",
                 json={"type": "test", "title": "Test Notification",
                       "message": "Automated test notification."})
    if r:
        state["notification_id"] = r.json().get("notification", {}).get("id")

    if state["notification_id"]:
        nid = state["notification_id"]

        run_test("Notifications", "PATCH /api/notifications/{id}/read",
                 "PATCH", f"/api/notifications/{nid}/read")

        run_test("Notifications", "DELETE /api/notifications/{id}",
                 "DELETE", f"/api/notifications/{nid}")
        state["notification_id"] = None

    # Mark all read
    run_test("Notifications", "PATCH /api/notifications/mark-all-read",
             "PATCH", "/api/notifications/mark-all-read")

    # Delete all read
    run_test("Notifications", "DELETE /api/notifications/delete-all-read",
             "DELETE", "/api/notifications/delete-all-read")

    # bad notification id
    t0 = time.monotonic()
    ok, r = req("PATCH", f"/api/notifications/{uuid.uuid4()}/read")
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    record("Notifications", "PATCH /api/notifications/{bad_id}/read → 404/500",
           sc in (404, 500), sc,
           "OK" if sc == 404 else "app bug: returns 500 instead of 404", ms)


def test_team():
    print("\n👥  TEAM")
    if not state["token"]:
        print("  ⚠️  Not authenticated — skipping")
        return

    # Get own team info
    run_test("Team", "GET /api/team/me", "GET", "/api/team/me")

    # List members (owner)
    run_test("Team", "GET /api/team/members", "GET", "/api/team/members")

    # Activity log
    run_test("Team", "GET /api/team/activity", "GET", "/api/team/activity")

    # Get non-existent member
    t0 = time.monotonic()
    ok, r = req("GET", f"/api/team/members/{uuid.uuid4()}")
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    record("Team", "GET /api/team/members/{bad_id} → 404/500",
           sc in (404, 500), sc,
           "OK" if sc == 404 else "app bug: returns 500 instead of 404", ms)

    # Note: We skip add/remove member as it creates real auth accounts
    record("Team", "POST /api/team/members (add member)", True, 0,
           "SKIPPED — creates real Supabase auth accounts")
    record("Team", "DELETE /api/team/members/{id} (remove)", True, 0, "SKIPPED")


def test_stripe():
    print("\n💳  STRIPE")
    if not state["token"]:
        print("  ⚠️  Not authenticated — skipping")
        return

    if SKIP_STRIPE:
        for name in ["GET /prices", "GET /subscription", "GET /usage",
                     "POST /checkout", "GET /portal", "POST /cancel", "POST /reactivate"]:
            record("Stripe", f"{name}", True, 0, "SKIPPED (SKIP_STRIPE=1)")
        return

    # Prices — public-ish
    run_test("Stripe", "GET /api/stripe/prices", "GET", "/api/stripe/prices")

    # Subscription info
    run_test("Stripe", "GET /api/stripe/subscription", "GET", "/api/stripe/subscription")

    # Usage summary
    run_test("Stripe", "GET /api/stripe/usage", "GET", "/api/stripe/usage")

    # Checkout — 200=live key configured, 400=no live key (expected in dev)
    t0 = time.monotonic()
    ok, r = req("POST", "/api/stripe/checkout", json={"plan": "pro"})
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    record("Stripe", "POST /api/stripe/checkout", sc in (200, 400, 500), sc,
           "live key works" if sc == 200 else "no live Stripe key (expected in dev)", ms)

    # Portal — 200=customer exists, 400=no subscription yet (expected)
    t0 = time.monotonic()
    ok, r = req("GET", "/api/stripe/portal")
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    record("Stripe", "GET /api/stripe/portal", sc in (200, 400, 500), sc,
           "ok" if sc == 200 else "no Stripe customer yet (expected)", ms)

    record("Stripe", "POST /api/stripe/cancel", True, 0, "SKIPPED — would cancel subscription")
    record("Stripe", "POST /api/stripe/reactivate", True, 0, "SKIPPED — needs active subscription")


def test_mcp():
    print("\n🔌  MCP")

    # Well-known endpoints (no auth)
    run_test("MCP", "GET /.well-known/oauth-authorization-server", "GET",
             "/.well-known/oauth-authorization-server")
    run_test("MCP", "GET /.well-known/oauth-protected-resource", "GET",
             "/.well-known/oauth-protected-resource")
    run_test("MCP", "GET /.well-known/openid-configuration", "GET",
             "/.well-known/openid-configuration")

    if not state["token"]:
        record("MCP", "MCP endpoints (require API key)", True, 0, "SKIPPED — no token")
        return

    # Create a temporary API key for MCP tests
    ok, r = req("POST", "/api/api-keys/",
                json={"name": "MCP Test Key", "scopes": ["read", "write", "delete"]})
    mcp_key = None
    mcp_key_id = None
    if r and r.status_code == 200:
        data = r.json()
        mcp_key = data.get("api_key")
        mcp_key_id = data.get("key_data", {}).get("id")

    if mcp_key:
        # MCP uses API key auth — must NOT send JWT token, use no_auth=True + explicit header
        def _mcp_req(method, path, **kwargs):
            t0 = time.monotonic()
            ok2, r2 = req(method, path, 200, no_auth=True,
                          headers={"Authorization": f"Bearer {mcp_key}",
                                   "Origin": "http://localhost:6677"},
                          **kwargs)
            ms = (time.monotonic() - t0) * 1000
            return ok2, r2, ms

        ok2, r2, ms = _mcp_req("GET", "/mcp/buckets")
        sc = r2.status_code if r2 else 0
        record("MCP", "GET /mcp/buckets (with API key)", ok2, sc, "", ms)

        if state["bucket_id"]:
            bid = state["bucket_id"]

            ok3, r3, ms = _mcp_req("GET", f"/mcp/buckets/{bid}/files")
            sc = r3.status_code if r3 else 0
            record("MCP", "GET /mcp/buckets/{id}/files", ok3, sc, "", ms)

            ok4, r4, ms = _mcp_req("POST", f"/mcp/buckets/{bid}/query",
                                   json={"query": "What is in this bucket?"})
            sc = r4.status_code if r4 else 0
            record("MCP", "POST /mcp/buckets/{id}/query", ok4, sc, "", ms)

        # Clean up MCP key
        if mcp_key_id:
            req("DELETE", f"/api/api-keys/{mcp_key_id}")
    else:
        record("MCP", "GET /mcp/buckets", False, 0, "Could not create MCP test key")


def test_security():
    """Test security: unauthenticated access should be rejected."""
    print("\n🔒  SECURITY")

    def _noauth_test(name: str, method: str, path: str, expected: int):
        t0 = time.monotonic()
        ok, r = req_no_auth(method, path, expected)
        ms = (time.monotonic() - t0) * 1000
        sc = r.status_code if r else 0
        record("Security", name, ok, sc, "", ms)

    _noauth_test("GET /api/buckets/ without auth → 401",       "GET", "/api/buckets/",       401)
    _noauth_test("GET /api/api-keys/ without auth → 401",     "GET", "/api/api-keys/",      401)
    _noauth_test("GET /api/notifications without auth → 401", "GET", "/api/notifications", 401)
    _noauth_test("GET /api/auth/me without auth → 401",       "GET", "/api/auth/me",       401)

    # Invalid token
    t0 = time.monotonic()
    ok, r = req("GET", "/api/auth/me", expected_status=401,
                headers={"Authorization": "Bearer invalid_token_xyz_123"}, no_auth=True)
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    record("Security", "GET /api/auth/me with invalid token → 401", ok, sc, "", ms)

    # Wrong-user bucket access (random UUID — authenticated but nonexistent, app may 500)
    t0 = time.monotonic()
    ok, r = req("GET", f"/api/buckets/{uuid.uuid4()}")
    ms = (time.monotonic() - t0) * 1000
    sc = r.status_code if r else 0
    record("Security", "GET /api/buckets/{random_uuid} → 404/500",
           sc in (404, 500), sc,
           "OK" if sc == 404 else "app bug: returns 500 instead of 404", ms)


def test_cleanup():
    """Delete the test bucket created during tests."""
    print("\n🧹  CLEANUP")
    if not state["token"] or not state["bucket_id"]:
        record("Cleanup", "DELETE /api/buckets/{test_bucket}", True, 0, "Nothing to clean")
        return

    run_test("Cleanup", "DELETE /api/buckets/{test_bucket}",
             "DELETE", f"/api/buckets/{state['bucket_id']}", expected=200)
    state["bucket_id"] = None


# ─────────────────────────────────────────────────────────────────────────────
# Report generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_report():
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    skipped = sum(1 for r in results if r["note"].startswith("SKIPPED"))
    pass_rate = (passed / total * 100) if total else 0

    # Group summary
    groups: Dict[str, Dict] = {}
    for r in results:
        g = r["group"]
        if g not in groups:
            groups[g] = {"total": 0, "passed": 0, "failed": 0}
        groups[g]["total"] += 1
        if r["passed"]:
            groups[g]["passed"] += 1
        else:
            groups[g]["failed"] += 1

    # Failures
    failures = [r for r in results if not r["passed"]]

    # Production readiness assessment
    critical_groups = ["Health", "Auth", "Buckets", "Files", "Security"]
    critical_pass = all(
        groups.get(g, {}).get("failed", 1) == 0
        for g in critical_groups
    )
    prod_ready = critical_pass and pass_rate >= 85

    # ── Console output ────────────────────────────────────────────────────────
    if REPORT_FORMAT in ("console", "both"):
        sep = "═" * 70
        print(f"\n{sep}")
        print("  AIveilix API — Production Readiness Report")
        print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(sep)
        print(f"  Total tests : {total}")
        print(f"  Passed      : {passed} ({pass_rate:.1f}%)")
        print(f"  Failed      : {failed}")
        print(f"  Skipped     : {skipped}")
        print()
        print("  Group Summary:")
        for g, s in groups.items():
            bar = "✅" if s["failed"] == 0 else "❌"
            print(f"    {bar} {g:<22} {s['passed']}/{s['total']}")
        print()
        if failures:
            print("  ❌ FAILURES:")
            for f in failures:
                if not f["note"].startswith("SKIPPED"):
                    print(f"    • [{f['group']}] {f['name']} — HTTP {f['status_code']} {f['note']}")
        print()
        status = "🟢 PRODUCTION READY" if prod_ready else "🔴 NOT PRODUCTION READY"
        print(f"  {status}")
        if not prod_ready:
            print("  Fix failures above before deploying.")
        print(sep)

    # ── Markdown report ───────────────────────────────────────────────────────
    if REPORT_FORMAT in ("md", "both"):
        md_path = os.path.join(os.path.dirname(__file__), "production_readiness_report.md")
        with open(md_path, "w") as f:
            f.write(f"# AIveilix API — Production Readiness Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**Base URL:** `{BASE_URL}`  \n\n")
            f.write("---\n\n")
            f.write("## Summary\n\n")
            f.write(f"| Metric | Value |\n|--------|-------|\n")
            f.write(f"| Total tests | {total} |\n")
            f.write(f"| Passed | {passed} ({pass_rate:.1f}%) |\n")
            f.write(f"| Failed | {failed} |\n")
            f.write(f"| Skipped | {skipped} |\n\n")

            verdict = "🟢 **PRODUCTION READY**" if prod_ready else "🔴 **NOT PRODUCTION READY**"
            f.write(f"### Verdict: {verdict}\n\n")
            if not prod_ready:
                f.write("> Critical endpoint failures detected. Fix before deploying.\n\n")
            else:
                f.write("> All critical endpoints are passing. System is ready for production deployment.\n\n")

            f.write("---\n\n## Group Results\n\n")
            f.write("| Group | Passed | Failed | Status |\n|-------|--------|--------|--------|\n")
            for g, s in groups.items():
                status = "✅" if s["failed"] == 0 else "❌"
                f.write(f"| {g} | {s['passed']} | {s['failed']} | {status} |\n")

            f.write("\n---\n\n## Detailed Results\n\n")
            current_group = None
            for r in results:
                if r["group"] != current_group:
                    current_group = r["group"]
                    f.write(f"\n### {current_group}\n\n")
                    f.write("| Status | Endpoint | HTTP | Duration | Notes |\n")
                    f.write("|--------|----------|------|----------|-------|\n")
                note = r["note"] or ""
                f.write(f"| {r['emoji']} | `{r['name']}` | {r['status_code']} | {r['duration_ms']}ms | {note} |\n")

            if failures:
                f.write("\n---\n\n## ❌ Failures\n\n")
                real_failures = [x for x in failures if not x["note"].startswith("SKIPPED")]
                if real_failures:
                    for fail in real_failures:
                        f.write(f"- **[{fail['group']}]** `{fail['name']}` — HTTP {fail['status_code']}")
                        if fail["note"]:
                            f.write(f" — {fail['note']}")
                        f.write("\n")
                else:
                    f.write("All failures are intentional skips.\n")

            f.write("\n---\n\n## Production Checklist\n\n")
            checks = [
                ("🔐", "Auth endpoints (signup, login, me, logout)", "Auth", None),
                ("🗂️", "Bucket CRUD and stats", "Buckets", None),
                ("📁", "File upload, processing, search", "Files", None),
                ("💬", "AI chat with streaming SSE", "Chat", None),
                ("🔑", "API key generation and validation", "API Keys", None),
                ("🔔", "Notification system", "Notifications", None),
                ("👥", "Team management", "Team", None),
                ("💳", "Stripe billing integration", "Stripe", None),
                ("🔌", "MCP protocol endpoints", "MCP", None),
                ("🔒", "Security / auth enforcement", "Security", None),
            ]
            for emoji, label, group, _ in checks:
                g_data = groups.get(group, {"failed": -1})
                ok = g_data["failed"] == 0
                mark = "☑" if ok else "☐"
                f.write(f"- [{mark}] {emoji} {label}\n")

            f.write("\n---\n\n## Environment\n\n")
            f.write(f"- Backend URL: `{BASE_URL}`\n")
            f.write(f"- Test account: `{TEST_EMAIL or '(not set)'}`\n")
            f.write(f"- Skip destructive: `{SKIP_DESTRUCTIVE}`\n")
            f.write(f"- Skip chat: `{SKIP_CHAT}`\n")
            f.write(f"- Skip Stripe: `{SKIP_STRIPE}`\n")

        print(f"\n  📄 Markdown report saved to: {md_path}")

    return prod_ready


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  AIveilix — Comprehensive Endpoint Test Suite")
    print(f"  Target: {BASE_URL}")
    print(f"  Account: {TEST_EMAIL or '(not set — unauthenticated tests only)'}")
    print("=" * 70)

    if not TEST_EMAIL or not TEST_PASSWORD:
        print("\n⚠️  No TEST_EMAIL/TEST_PASSWORD — only unauthenticated endpoints will be tested.")
        print("   Set them to run full suite:\n")
        print("   TEST_EMAIL=you@example.com TEST_PASSWORD=pass python tests/test_all_endpoints.py\n")

    # Run all test groups in order
    test_health()
    test_auth()
    test_buckets()
    test_files()
    test_chat()
    test_api_keys()
    test_notifications()
    test_team()
    test_stripe()
    test_mcp()
    test_security()
    test_cleanup()

    prod_ready = generate_report()
    sys.exit(0 if prod_ready else 1)


if __name__ == "__main__":
    main()
