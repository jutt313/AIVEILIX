"""
Demo session resolution — the ``get_demo_session`` FastAPI dependency.

Validates the demo token, loads the ``DemoLink`` + ``DemoLead`` it points at, and
enforces that the demo is still live (active + unexpired). Everything downstream
reads the bucket from ``session.demo_link.bucket_id`` only, so a visitor can never
escape their one bucket.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.demo import DemoLead, DemoLink
from app.services.demo.tokens import decode_demo_token

demo_security = HTTPBearer(auto_error=False)


@dataclass
class DemoSession:
    demo_link: DemoLink
    demo_lead: DemoLead

    @property
    def bucket_id(self) -> uuid.UUID:
        return self.demo_link.bucket_id

    @property
    def link_id(self) -> uuid.UUID:
        return self.demo_link.id

    @property
    def lead_id(self) -> uuid.UUID:
        return self.demo_lead.id


def _is_expired(link: DemoLink) -> bool:
    if link.expires_at is None:
        return False
    expires = link.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return expires <= datetime.now(timezone.utc)


async def get_demo_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(demo_security),
    db: AsyncSession = Depends(get_db),
) -> DemoSession:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Demo session required.")

    payload = decode_demo_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Demo session expired or invalid.")

    try:
        link_id = uuid.UUID(payload["demo_link_id"])
        lead_id = uuid.UUID(payload["demo_lead_id"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Demo session invalid.")

    link = await db.get(DemoLink, link_id)
    if link is None or not link.is_active or _is_expired(link):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This demo is no longer available.")

    lead = await db.get(DemoLead, lead_id)
    if lead is None or lead.demo_link_id != link.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Demo session invalid.")

    return DemoSession(demo_link=link, demo_lead=lead)
