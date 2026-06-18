"""
Single source of truth for subscription plans, limits, the free trial, and
per-customer Enterprise overrides.

Self-serve: Individual ($15) and Team ($49). New accounts get a 15-day Individual trial.
Enterprise = plan 'business' + a per-account ``limits_override`` JSON blob set
by an admin (Option B). The base 'business' numbers below are only defaults —
each Enterprise customer's real limits come from their override.

Limits are sized so a max-usage month stays within the variable-cost cap on
the self-serve tiers (Individual <= ~$8, Team <= ~$20). Cost drivers: documents/pages
(OCR + summary), images (Kimi vision), in-app chat (LLM), storage (R2). MCP
runs on the user's own AI, so it is rate-limited rather than metered.

Enforced at: upload (docs/storage), pipeline (pages/images), chat (messages/mo),
team invite (seats), MCP request (rate). When the trial ends without payment the
account is 'locked' (data readable, new actions blocked).
"""

from __future__ import annotations

from dataclasses import dataclass, replace as dc_replace
from datetime import datetime, timedelta, timezone

_MB = 1024 ** 2
_GB = 1024 ** 3
_TB = 1024 ** 4

TRIAL_DAYS = 15
TRIAL_PLAN = "individual"
DEFAULT_PAID_PLAN = "individual"


@dataclass(frozen=True)
class PlanLimits:
    name: str               # display name shown in UI
    price_usd: int          # monthly price (0 for enterprise/locked — quoted per deal)
    max_users: int          # seats: owner + accepted members
    max_buckets: int
    max_documents: int      # total stored documents
    max_pages: int          # total processed pages — OCR/summary cost driver
    max_storage_bytes: int  # raw files + page screenshots in R2
    max_chat_messages: int  # in-app AI chats per calendar month
    mcp_rate_per_min: int   # MCP requests allowed per minute
    max_images: int         # total visual elements (Kimi vision cost driver)
    max_file_size_bytes: int  # largest single upload allowed (per-file cap)


PLAN_LIMITS: dict[str, PlanLimits] = {
    "individual": PlanLimits(
        name="Individual", price_usd=15,
        max_users=1, max_buckets=5, max_documents=100, max_pages=1_800,
        max_storage_bytes=5 * _GB, max_chat_messages=500, mcp_rate_per_min=30,
        max_images=400, max_file_size_bytes=100 * _MB,
    ),
    "team": PlanLimits(
        name="Team", price_usd=49,
        max_users=9, max_buckets=20, max_documents=300, max_pages=4_000,
        max_storage_bytes=15 * _GB, max_chat_messages=1_800, mcp_rate_per_min=60,
        max_images=1_200, max_file_size_bytes=5 * _GB,
    ),
    # Enterprise base — generous defaults; real per-customer numbers come from
    # the account's limits_override (set in the admin panel).
    "business": PlanLimits(
        name="Enterprise", price_usd=0,
        max_users=50, max_buckets=1_000, max_documents=100_000, max_pages=1_000_000,
        max_storage_bytes=1 * _TB, max_chat_messages=100_000, mcp_rate_per_min=600,
        max_images=1_000_000, max_file_size_bytes=100 * _GB,
    ),
}

# Trial-expired / cancelled accounts: data readable, every create action blocked.
LOCKED_LIMITS = PlanLimits(
    name="Locked", price_usd=0,
    max_users=1, max_buckets=0, max_documents=0, max_pages=0,
    max_storage_bytes=0, max_chat_messages=0, mcp_rate_per_min=0, max_images=0,
    max_file_size_bytes=0,
)

# Legacy enum values mapped onto current plans ('business' is now Enterprise).
_LEGACY_PLAN_ALIASES = {"free": "individual", "pro": "individual"}

# Fields an admin override may set per Enterprise customer.
_OVERRIDABLE = {
    "max_users", "max_buckets", "max_documents", "max_pages",
    "max_storage_bytes", "max_chat_messages", "mcp_rate_per_min", "max_images",
    "max_file_size_bytes",
}


@dataclass(frozen=True)
class EffectivePlan:
    plan: str                  # 'individual' | 'team' | 'business' | 'locked'
    limits: PlanLimits
    is_trial: bool
    trial_ends_at: datetime | None
    locked: bool


def trial_end_from(start: datetime | None = None) -> datetime:
    """Trial end = start (default now) + TRIAL_DAYS."""
    return (start or datetime.now(timezone.utc)) + timedelta(days=TRIAL_DAYS)


def normalize_plan_key(plan: str | None) -> str:
    """Return the canonical plan key used by current code."""
    raw = (plan or DEFAULT_PAID_PLAN).lower()
    return _LEGACY_PLAN_ALIASES.get(raw, raw)


def apply_override(base: PlanLimits, override: dict | None) -> PlanLimits:
    """Return base limits with any valid per-customer override values applied."""
    if not override or not isinstance(override, dict):
        return base
    changes: dict[str, int] = {}
    for key, value in override.items():
        # bool is a subclass of int — exclude it explicitly.
        if key in _OVERRIDABLE and isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0:
            changes[key] = int(value)
    return dc_replace(base, **changes) if changes else base


def resolve_effective_plan(sub, now: datetime | None = None) -> EffectivePlan:
    """
    Resolve a Subscription row (or None) into the limits that apply right now,
    including any per-customer Enterprise override.

    Precedence:
      1. Paid + active (Stripe)             -> that plan (+ override)
      2. Inside trial/grant window          -> that plan (+ override)
      3. Window passed, unpaid              -> locked
      4. Open-ended active grant (no Stripe) -> that plan (+ override)
      5. Otherwise                          -> locked
    """
    now = now or datetime.now(timezone.utc)

    if sub is None:
        return EffectivePlan(TRIAL_PLAN, PLAN_LIMITS[TRIAL_PLAN], True, None, False)

    plan = normalize_plan_key(getattr(sub, "plan", ""))
    has_paid = bool(getattr(sub, "stripe_subscription_id", None))
    status = getattr(sub, "status", "active")
    period_end = getattr(sub, "current_period_end", None)
    override = getattr(sub, "limits_override", None)

    def _eff(key: str, is_trial: bool, ends: datetime | None) -> EffectivePlan:
        base = PLAN_LIMITS.get(key, PLAN_LIMITS[DEFAULT_PAID_PLAN])
        plan_override = override if key == "business" else None
        return EffectivePlan(key, apply_override(base, plan_override), is_trial, ends, False)

    # 1. Paid subscriber.
    if has_paid and status == "active" and plan in PLAN_LIMITS:
        return _eff(plan, False, None)

    # 2 / 3. Trial or grant window.
    if period_end is not None:
        if period_end > now:
            return _eff(plan if plan in PLAN_LIMITS else TRIAL_PLAN, not has_paid, period_end)
        return EffectivePlan("locked", LOCKED_LIMITS, False, period_end, True)

    # 4. Open-ended active grant (e.g. an Enterprise account, no Stripe).
    if plan in PLAN_LIMITS and status == "active":
        return _eff(plan, False, None)

    # 5. Cancelled / past_due / unknown.
    return EffectivePlan("locked", LOCKED_LIMITS, False, period_end, True)


def get_plan_limits(plan: str | None) -> PlanLimits:
    """Base limits for a plan key (no trial/override logic). Falls back to Individual."""
    key = normalize_plan_key(plan)
    return PLAN_LIMITS.get(key, PLAN_LIMITS[DEFAULT_PAID_PLAN])
