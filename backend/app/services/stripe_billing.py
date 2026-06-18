"""
Stripe integration for self-serve subscriptions (Individual / Team).

Single place that talks to Stripe. Endpoints stay thin: they call
``create_checkout_session`` / ``cancel_subscription`` and feed raw webhook
bodies into ``construct_event`` + ``handle_event``.

Plan <-> price mapping comes from settings (the price IDs you create in the
Stripe Dashboard). Enterprise ('business') is sold manually and never goes
through Checkout, so it has no price here.

The webhook handlers are upserts keyed off the Stripe customer/subscription,
so redelivered events are safe to process twice.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.platform import Subscription
from app.services.notifications import create_notification

logger = logging.getLogger(__name__)

# Plans that can be bought self-serve. 'business' (Enterprise) is excluded.
SELF_SERVE_PLANS = ("individual", "team")


def _plan_to_price() -> dict[str, str]:
    return {
        "individual": settings.stripe_price_individual,
        "team": settings.stripe_price_team,
    }


def _price_to_plan() -> dict[str, str]:
    return {price: plan for plan, price in _plan_to_price().items() if price}


def is_configured() -> bool:
    return bool(settings.stripe_secret_key)


def _require_configured() -> None:
    if not settings.stripe_secret_key:
        raise RuntimeError("Stripe is not configured (STRIPE_SECRET_KEY missing).")
    stripe.api_key = settings.stripe_secret_key


def price_for_plan(plan: str) -> str:
    price = _plan_to_price().get(plan, "")
    if not price:
        raise ValueError(f"No Stripe price configured for plan '{plan}'.")
    return price


# --- Stripe status -> our subscription_status enum ----------------------------

def _map_status(stripe_status: str | None) -> str:
    if stripe_status in ("active", "trialing"):
        return "active"
    if stripe_status in ("canceled", "incomplete_expired"):
        return "cancelled"
    # past_due, unpaid, incomplete, paused -> treat as past_due (grace/dunning)
    return "past_due"


def _to_dt(unix_ts: int | None) -> datetime | None:
    if not unix_ts:
        return None
    return datetime.fromtimestamp(int(unix_ts), tz=timezone.utc)


def _sub_period_end(sub_obj: dict) -> datetime | None:
    """Period end moved onto items in newer API versions; fall back to top level."""
    items = (sub_obj.get("items") or {}).get("data") or []
    if items and items[0].get("current_period_end"):
        return _to_dt(items[0]["current_period_end"])
    return _to_dt(sub_obj.get("current_period_end"))


def _sub_price_id(sub_obj: dict) -> str | None:
    items = (sub_obj.get("items") or {}).get("data") or []
    if not items:
        return None
    price = items[0].get("price") or {}
    return price.get("id")


# --- Subscription row helpers -------------------------------------------------

async def _get_subscription(db: AsyncSession, owner_user_id: uuid.UUID) -> Subscription | None:
    return (
        await db.execute(select(Subscription).where(Subscription.user_id == owner_user_id))
    ).scalar_one_or_none()


async def _get_or_create_subscription(db: AsyncSession, owner_user_id: uuid.UUID) -> Subscription:
    sub = await _get_subscription(db, owner_user_id)
    if sub is None:
        sub = Subscription(user_id=owner_user_id, plan="free", status="active")
        db.add(sub)
        await db.flush()
    return sub


async def _find_by_stripe(
    db: AsyncSession,
    *,
    customer_id: str | None = None,
    subscription_id: str | None = None,
    owner_user_id: str | None = None,
) -> Subscription | None:
    """Locate our row from a webhook payload (metadata first, then Stripe ids)."""
    if owner_user_id:
        try:
            row = await _get_subscription(db, uuid.UUID(owner_user_id))
            if row:
                return row
        except (ValueError, TypeError):
            pass
    if subscription_id:
        row = (
            await db.execute(
                select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
            )
        ).scalar_one_or_none()
        if row:
            return row
    if customer_id:
        row = (
            await db.execute(
                select(Subscription).where(Subscription.stripe_customer_id == customer_id)
            )
        ).scalar_one_or_none()
        if row:
            return row
    return None


# --- Checkout -----------------------------------------------------------------

async def create_checkout_session(
    db: AsyncSession,
    owner_user_id: uuid.UUID,
    email: str,
    plan: str,
) -> str:
    """Create a Stripe Checkout session for a self-serve plan and return its URL."""
    _require_configured()
    if plan not in SELF_SERVE_PLANS:
        raise ValueError(f"Plan '{plan}' is not available for self-serve checkout.")
    price = price_for_plan(plan)

    sub = await _get_or_create_subscription(db, owner_user_id)
    base = settings.frontend_url.rstrip("/")
    metadata = {"owner_user_id": str(owner_user_id), "plan": plan}

    params: dict = {
        "mode": "subscription",
        "line_items": [{"price": price, "quantity": 1}],
        "client_reference_id": str(owner_user_id),
        "metadata": metadata,
        "subscription_data": {"metadata": metadata},
        "success_url": f"{base}/?billing=success&session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{base}/?billing=cancelled",
        "allow_promotion_codes": True,
    }
    # Reuse the saved customer if we have one, otherwise let Checkout create it.
    if sub.stripe_customer_id:
        params["customer"] = sub.stripe_customer_id
    else:
        params["customer_email"] = email

    session = await asyncio.to_thread(stripe.checkout.Session.create, **params)
    await db.commit()
    return session.url


async def create_portal_session(
    db: AsyncSession,
    owner_user_id: uuid.UUID,
) -> str:
    """Stripe Customer Portal — lets the user change card / cancel / downgrade."""
    _require_configured()
    sub = await _get_subscription(db, owner_user_id)
    if not sub or not sub.stripe_customer_id:
        raise ValueError("No Stripe customer for this account yet.")
    base = settings.frontend_url.rstrip("/")
    session = await asyncio.to_thread(
        stripe.billing_portal.Session.create,
        customer=sub.stripe_customer_id,
        return_url=f"{base}/?billing=portal",
    )
    return session.url


async def cancel_subscription(
    db: AsyncSession,
    owner_user_id: uuid.UUID,
    at_period_end: bool = True,
) -> None:
    """Cancel in Stripe. Default keeps access until the period ends."""
    _require_configured()
    sub = await _get_subscription(db, owner_user_id)
    if not sub or not sub.stripe_subscription_id:
        raise ValueError("No active Stripe subscription to cancel.")
    if at_period_end:
        await asyncio.to_thread(
            stripe.Subscription.modify, sub.stripe_subscription_id, cancel_at_period_end=True
        )
    else:
        await asyncio.to_thread(stripe.Subscription.delete, sub.stripe_subscription_id)


# --- Webhook ------------------------------------------------------------------

def construct_event(payload: bytes, sig_header: str) -> stripe.Event:
    """Verify the Stripe signature and return the parsed event."""
    if not settings.stripe_webhook_secret:
        raise RuntimeError("Stripe webhook secret not configured.")
    return stripe.Webhook.construct_event(
        payload, sig_header, settings.stripe_webhook_secret
    )


async def handle_event(db: AsyncSession, event: stripe.Event) -> None:
    """Apply a verified Stripe event to our subscriptions table."""
    etype = event["type"]
    obj = event["data"]["object"]
    handler = {
        "checkout.session.completed": _on_checkout_completed,
        "customer.subscription.created": _on_subscription_change,
        "customer.subscription.updated": _on_subscription_change,
        "customer.subscription.deleted": _on_subscription_deleted,
        "customer.subscription.trial_will_end": _on_trial_will_end,
        "invoice.paid": _on_invoice_paid,
        "invoice.payment_failed": _on_invoice_failed,
    }.get(etype)

    if handler is None:
        logger.info("stripe webhook: ignoring unhandled event %s", etype)
        return
    await handler(db, obj)
    await db.commit()


async def _on_checkout_completed(db: AsyncSession, session: dict) -> None:
    meta = session.get("metadata") or {}
    owner_user_id = meta.get("owner_user_id") or session.get("client_reference_id")
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    plan = meta.get("plan")

    sub = await _find_by_stripe(
        db, customer_id=customer_id, subscription_id=subscription_id, owner_user_id=owner_user_id
    )
    if sub is None:
        logger.warning("stripe checkout.completed: no subscription row for %s", owner_user_id)
        return

    sub.stripe_customer_id = customer_id or sub.stripe_customer_id
    sub.stripe_subscription_id = subscription_id or sub.stripe_subscription_id
    if plan in SELF_SERVE_PLANS:
        sub.plan = plan
    sub.status = "active"

    # Pull the real period end from the subscription object.
    if subscription_id:
        try:
            _require_configured()
            full = await asyncio.to_thread(stripe.Subscription.retrieve, subscription_id)
            sub.current_period_end = _sub_period_end(full)
            price_plan = _price_to_plan().get(_sub_price_id(full) or "")
            if price_plan:
                sub.plan = price_plan
        except Exception as exc:  # noqa: BLE001 - best effort enrichment
            logger.warning("stripe checkout.completed: could not retrieve sub: %s", exc)

    await create_notification(
        db, str(sub.user_id), "success",
        "Subscription active",
        f"Your {sub.plan.capitalize()} plan is now active. Thanks for subscribing!",
    )


async def _on_subscription_change(db: AsyncSession, sub_obj: dict) -> None:
    meta = sub_obj.get("metadata") or {}
    sub = await _find_by_stripe(
        db,
        customer_id=sub_obj.get("customer"),
        subscription_id=sub_obj.get("id"),
        owner_user_id=meta.get("owner_user_id"),
    )
    if sub is None:
        logger.warning("stripe subscription change: no row for %s", sub_obj.get("id"))
        return

    sub.stripe_subscription_id = sub_obj.get("id") or sub.stripe_subscription_id
    sub.stripe_customer_id = sub_obj.get("customer") or sub.stripe_customer_id
    sub.status = _map_status(sub_obj.get("status"))
    sub.current_period_end = _sub_period_end(sub_obj) or sub.current_period_end

    price_plan = _price_to_plan().get(_sub_price_id(sub_obj) or "")
    if price_plan:  # captures upgrade AND downgrade
        sub.plan = price_plan


async def _on_subscription_deleted(db: AsyncSession, sub_obj: dict) -> None:
    meta = sub_obj.get("metadata") or {}
    sub = await _find_by_stripe(
        db,
        customer_id=sub_obj.get("customer"),
        subscription_id=sub_obj.get("id"),
        owner_user_id=meta.get("owner_user_id"),
    )
    if sub is None:
        return
    sub.status = "cancelled"
    sub.current_period_end = _sub_period_end(sub_obj) or sub.current_period_end
    await create_notification(
        db, str(sub.user_id), "warning",
        "Subscription ended",
        "Your subscription has ended. Your data stays readable, but new actions are paused until you resubscribe.",
    )


async def _on_trial_will_end(db: AsyncSession, sub_obj: dict) -> None:
    meta = sub_obj.get("metadata") or {}
    sub = await _find_by_stripe(
        db,
        customer_id=sub_obj.get("customer"),
        subscription_id=sub_obj.get("id"),
        owner_user_id=meta.get("owner_user_id"),
    )
    if sub is None:
        return
    await create_notification(
        db, str(sub.user_id), "info",
        "Trial ending soon",
        "Your trial ends in a few days. Add a payment method to keep your plan active.",
    )


async def _on_invoice_paid(db: AsyncSession, invoice: dict) -> None:
    sub = await _find_by_stripe(
        db,
        customer_id=invoice.get("customer"),
        subscription_id=invoice.get("subscription"),
    )
    if sub is None:
        return
    sub.status = "active"
    # Extend the period from the invoice line, if present.
    lines = (invoice.get("lines") or {}).get("data") or []
    period = lines[0].get("period") if lines else None
    if period and period.get("end"):
        sub.current_period_end = _to_dt(period["end"])


async def _on_invoice_failed(db: AsyncSession, invoice: dict) -> None:
    sub = await _find_by_stripe(
        db,
        customer_id=invoice.get("customer"),
        subscription_id=invoice.get("subscription"),
    )
    if sub is None:
        return
    sub.status = "past_due"
    await create_notification(
        db, str(sub.user_id), "warning",
        "Payment failed",
        "We couldn't process your subscription payment. Please update your card to avoid losing access.",
    )
