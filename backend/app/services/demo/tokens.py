"""
Demo session token — the one new auth primitive for the public demo layer.

Signed, stateless JWT. Claims: ``demo_link_id``, ``demo_lead_id``, ``type=demo``,
``exp``. Issued on a successful code+identity entry (primary lead) or invite-link
accept (team member). Scoped to ONE bucket — it can never reach another bucket or
any real user/billing data, because every demo endpoint resolves the bucket from
the token's ``demo_link_id`` only.
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings

DEMO_TOKEN_TYPE = "demo"
DEMO_TOKEN_TTL_HOURS = 4


def create_demo_token(demo_link_id: str, demo_lead_id: str, *, ttl_hours: int = DEMO_TOKEN_TTL_HOURS) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
    payload = {
        "demo_link_id": str(demo_link_id),
        "demo_lead_id": str(demo_lead_id),
        "type": DEMO_TOKEN_TYPE,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_demo_token(token: str) -> dict | None:
    """Return the decoded claims for a valid demo token, else None.

    Rejects anything that isn't explicitly a demo token so a normal user access
    token can never be replayed against the demo endpoints (and vice-versa).
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
    if payload.get("type") != DEMO_TOKEN_TYPE:
        return None
    if not payload.get("demo_link_id") or not payload.get("demo_lead_id"):
        return None
    return payload
