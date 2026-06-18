"""
Enterprise "Contact sales" inquiries.

POST /v1/enterprise/contact — authenticated. Saves the inquiry, notifies the
requester ("we'll be in contact shortly"), and emails the details to the sales
inbox. The optional meeting_url lets the customer share a calendar/booking link.
"""

import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.config import settings
from app.database import get_db
from app.models.platform import EnterpriseInquiry
from app.models.user import Profile, User
from app.services.email import send_enterprise_inquiry
from app.services.notifications import create_notification

router = APIRouter(prefix="/enterprise", tags=["enterprise"])


class EnterpriseContactRequest(BaseModel):
    company: str | None = None
    role: str | None = None
    team_size: str | None = None
    doc_volume: str | None = None
    use_case: str | None = None
    meeting_url: str | None = None


def _clean(value: str | None) -> str | None:
    return (value or "").strip() or None


def _admin_recipients() -> list[str]:
    recipients = [e.strip() for e in (settings.admin_emails or "").split(",") if e.strip()]
    fallback = (settings.smtp_from_email or "").strip()
    if fallback and not recipients:
        recipients.append(fallback)
    seen: set[str] = set()
    unique: list[str] = []
    for email in recipients:
        key = email.lower()
        if key not in seen:
            seen.add(key)
            unique.append(email)
    return unique


@router.post("/contact")
async def enterprise_contact(
    body: EnterpriseContactRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = uuid.UUID(current_user["user_id"])

    inquiry = EnterpriseInquiry(
        user_id=user_id,
        company=_clean(body.company),
        role=_clean(body.role),
        team_size=_clean(body.team_size),
        doc_volume=_clean(body.doc_volume),
        use_case=_clean(body.use_case),
        meeting_url=_clean(body.meeting_url),
    )
    db.add(inquiry)

    user = await db.get(User, user_id)
    requester_email = user.email if user else "unknown"
    profile = (
        await db.execute(select(Profile).where(Profile.user_id == user_id))
    ).scalar_one_or_none()
    requester_name = profile.full_name if profile else None
    submitted_at = datetime.now(timezone.utc)

    await create_notification(
        db, str(user_id), "success",
        "Enterprise request received",
        "Thanks — our team will be in contact shortly by email.",
    )
    await db.commit()
    await db.refresh(inquiry)

    # Best-effort: email the inquiry to the sales inbox.
    try:
        payload = {
            "request_id": str(inquiry.id),
            "submitted_at": inquiry.created_at.isoformat() if inquiry.created_at else submitted_at.isoformat(),
            "requester_name": requester_name,
            "requester_email": requester_email,
            "user_id": str(user_id),
            "company": inquiry.company,
            "role": inquiry.role,
            "team_size": inquiry.team_size,
            "doc_volume": inquiry.doc_volume,
            "use_case": inquiry.use_case,
            "meeting_url": inquiry.meeting_url,
        }
        for to in _admin_recipients():
            await asyncio.to_thread(send_enterprise_inquiry, to, payload)
    except Exception:
        pass  # never fail the request because email delivery hiccuped

    return {"ok": True, "message": "Thanks — we'll be in contact shortly by email."}
