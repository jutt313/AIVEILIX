# Aiveilix — Authentication

> This document describes the complete authentication system for Aiveilix. It covers email and password auth, Google and GitHub OAuth, JWT token management, two-factor authentication, session handling, logout, and rate limiting.

---

## Overview

Aiveilix supports three ways to sign in:

| Method | Description |
|---|---|
| **Email + Password** | Custom auth with bcrypt hashing and JWT |
| **Google OAuth** | Sign in with Google account |
| **GitHub OAuth** | Sign in with GitHub account |

All methods issue the same JWT access token and refresh token upon success.

---

## 1. Email and Password Auth

### Registration Flow

```
User submits email + password
        |
        v
FastAPI validates input (email format, password strength)
        |
        v
Check if email already exists in PostgreSQL (users table)
        |
        v
Hash password with bcrypt (cost factor: 12)
        |
        v
Create user record in PostgreSQL (users table)
Create profile record in PostgreSQL (profiles table)
Create free plan subscription in PostgreSQL (subscriptions table)
        |
        v
Send verification email with secure link
        |
        v
Issue JWT access token + refresh token
        |
        v
Return tokens to frontend
```

**Example user record created:**
```json
{
  "id": "u_abc123",
  "email": "user@example.com",
  "password_hash": "$2b$12$...",
  "provider": "email",
  "is_verified": false,
  "is_active": true,
  "created_at": "2026-03-01T10:00:00Z"
}
```

---

### Login Flow

```
User submits email + password
        |
        v
Check failed_attempts in Redis
If 5 or more failed attempts in last 1 hour → block login
Show clean message: "Too many failed attempts. Please try again in 1 hour."
        |
        v
Look up user by email in PostgreSQL
        |
        v
Verify password against bcrypt hash
        |
        v
If wrong password:
  Increment failed_attempts counter in Redis
  Return clean error message
        |
        v
If correct:
  Reset failed_attempts counter in Redis
  Issue JWT access token (24 hours)
  Issue refresh token (30 days) → save in Redis
  Return tokens to frontend
```

---

## 2. Google OAuth Flow

```
User clicks "Sign in with Google"
        |
        v
Frontend redirects to Google OAuth consent screen
        |
        v
User approves → Google redirects back to:
https://api.aiveilix.com/auth/google/callback?code=...
        |
        v
FastAPI exchanges code for Google access token
        |
        v
FastAPI fetches user info from Google (email, name, avatar)
        |
        v
Check if user exists in PostgreSQL by email
  If yes → log in existing user
  If no → create new user record (provider: google)
        |
        v
Save token to oauth_tokens table in PostgreSQL
        |
        v
Issue JWT access token + refresh token
        |
        v
Return tokens to frontend
```

---

## 3. GitHub OAuth Flow

Same flow as Google OAuth, with GitHub as the provider.

```
User clicks "Sign in with GitHub"
        |
        v
Frontend redirects to GitHub OAuth consent screen
        |
        v
User approves → GitHub redirects back to:
https://api.aiveilix.com/auth/github/callback?code=...
        |
        v
FastAPI exchanges code for GitHub access token
Fetches user info from GitHub (email, name, avatar)
        |
        v
Check if user exists in PostgreSQL by email
  If yes → log in existing user
  If no → create new user record (provider: github)
        |
        v
Save token to oauth_tokens table in PostgreSQL
        |
        v
Issue JWT access token + refresh token
        |
        v
Return tokens to frontend
```

---

## 4. JWT Token Management

### Access Token

| Property | Value |
|---|---|
| Type | JWT (JSON Web Token) |
| Expiry | 24 hours |
| Storage | Frontend memory (never localStorage) |
| Contains | `user_id`, `email`, `plan`, `exp` |

**Example JWT payload:**
```json
{
  "user_id": "u_abc123",
  "email": "user@example.com",
  "plan": "individual",
  "exp": 1743120000
}
```

---

### Refresh Token

| Property | Value |
|---|---|
| Expiry | 30 days |
| Storage | Redis + HttpOnly cookie |
| Purpose | Issue new access token without re-login |

### Token Refresh Flow

```
Access token expires (after 24 hours)
        |
        v
Frontend sends refresh token to:
POST /auth/refresh
        |
        v
FastAPI validates refresh token in Redis
        |
        v
If valid → issue new access token (24 hours)
If invalid or expired → force user to log in again
```

---

### Protected Routes

Every protected API endpoint checks the JWT token via FastAPI middleware.

**Example FastAPI dependency:**
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## 5. Two-Factor Authentication (2FA)

Two-factor authentication is enabled from the start. Users can activate it from their profile settings.

### How It Works

Aiveilix uses **TOTP** (Time-based One-Time Password) — compatible with Google Authenticator, Authy, and any standard TOTP app.

### Database Columns Added to `users`

| Column | Type | Description |
|---|---|---|
| `two_factor_enabled` | BOOLEAN | Whether 2FA is active for this user |
| `two_factor_secret` | VARCHAR | TOTP secret key (encrypted at rest) |
| `two_factor_backup_codes` | JSONB | Array of one-time backup codes |

---

### 2FA Setup Flow

```
User goes to Profile → Security → Enable 2FA
        |
        v
Backend generates a TOTP secret using pyotp
        |
        v
Backend returns QR code to frontend
        |
        v
User scans QR code with Google Authenticator or Authy
        |
        v
User enters the 6-digit code from their app
        |
        v
Backend verifies the code
        |
        v
If correct:
  Save two_factor_secret to users table (encrypted)
  Set two_factor_enabled = true
  Generate 8 backup codes → save to two_factor_backup_codes
  Show backup codes to user once (user must save them)
```

**Example using pyotp:**
```python
import pyotp

# Generate secret
secret = pyotp.random_base32()

# Generate QR code URI
totp = pyotp.TOTP(secret)
uri = totp.provisioning_uri(name="user@example.com", issuer_name="Aiveilix")

# Verify code entered by user
is_valid = totp.verify("123456")
```

---

### 2FA Login Flow

```
User enters email + password (correct)
        |
        v
Backend checks two_factor_enabled
        |
        v
If 2FA enabled:
  Return response: { "requires_2fa": true, "temp_token": "..." }
        |
        v
Frontend shows 2FA code input screen
        |
        v
User enters 6-digit code from their app
        |
        v
Backend verifies TOTP code using pyotp
        |
        v
If correct → issue full JWT access token + refresh token
If incorrect → return clean error message
```

---

### 2FA Backup Codes

If a user loses access to their authenticator app, they can use one of their 8 backup codes to log in. Each backup code can only be used once.

```
User enters backup code instead of TOTP code
        |
        v
Backend checks code against two_factor_backup_codes in PostgreSQL
        |
        v
If valid → mark code as used, issue JWT tokens
If invalid → return clean error message
```

---

### Disabling 2FA

```
User goes to Profile → Security → Disable 2FA
        |
        v
User must enter current TOTP code to confirm
        |
        v
Backend verifies code
        |
        v
Set two_factor_enabled = false
Clear two_factor_secret and backup codes
```

---

## 6. Logout

```
User clicks logout
        |
        v
Frontend sends request to:
POST /auth/logout
        |
        v
Backend adds current JWT to Redis blacklist
Key: blacklist:{token_jti}
TTL: matches remaining token expiry time
        |
        v
Backend deletes refresh token from Redis
        |
        v
Frontend clears tokens from memory
        |
        v
User redirected to landing page
```

**Why blacklist in Redis?**
JWT tokens cannot be invalidated after they are issued. Adding the token ID (`jti`) to a Redis blacklist ensures the token is rejected on every subsequent request, even before it expires.

---

## 7. Rate Limiting on Login

To prevent brute force attacks, login attempts are rate limited per email address.

| Rule | Value |
|---|---|
| Max failed attempts | 5 per hour |
| Lock duration | 1 hour |
| Counter storage | Redis |
| Reset on successful login | Yes |

### Redis Keys

```
failed_login:{email} → integer (count of failed attempts)
TTL: 1 hour (resets automatically)
```

### Clean Message Shown to User

```
"Too many failed login attempts. Please try again in 1 hour.
 If you need help, contact support."
```

**Example rate limit check in FastAPI:**
```python
import redis

r = redis.Redis()

async def check_rate_limit(email: str):
    key = f"failed_login:{email}"
    attempts = r.get(key)

    if attempts and int(attempts) >= 5:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please try again in 1 hour."
        )

async def record_failed_attempt(email: str):
    key = f"failed_login:{email}"
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, 3600)  # 1 hour TTL
    pipe.execute()

async def reset_failed_attempts(email: str):
    r.delete(f"failed_login:{email}")
```

---

## 8. Password Reset Flow

```
User clicks "Forgot Password"
        |
        v
User enters their email address
        |
        v
Backend checks if email exists in PostgreSQL
        |
        v
If exists:
  Generate secure reset token (UUID)
  Save to Redis with 1 hour TTL:
  Key: password_reset:{token} → user_id
  Send email with reset link:
  https://aiveilix.com/reset-password?token={token}
        |
        v
User clicks link → enters new password
        |
        v
Backend validates token from Redis
        |
        v
Hash new password with bcrypt
Update password_hash in PostgreSQL
Delete reset token from Redis
        |
        v
User redirected to login page
```

---

## Full Auth Flow Summary

```
Register / Login
        |
        v
Email+Password or Google or GitHub
        |
        v
2FA check (if enabled)
        |
        v
JWT access token (24hrs) + Refresh token (30 days)
        |
        v
Every API request:
  Redis checks JWT not blacklisted
  FastAPI middleware validates JWT
        |
        v
Access token expires after 24hrs:
  Refresh token issues new access token
        |
        v
Logout:
  JWT blacklisted in Redis
  Refresh token deleted
```

---

*Document version: 1.0 — March 2026*
