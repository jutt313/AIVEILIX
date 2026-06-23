"""
Public Demo Bucket layer.

A thin, isolated set of tables that wrap a real (``is_demo=true``) bucket so we can
run per-company public "try-on-your-docs" demo pages. Demo visitors are NOT
``users`` — they live entirely in ``demo_leads`` and can only ever reach the one
bucket their ``demo_link`` points at. The whole layer is designed to be dropped
after the outreach campaign without touching core product tables.

See formarketing/DEMO_BUCKET_DEV_PLAN.md for the full design.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class DemoLink(Base):
    """The demo config that wraps one real bucket. One code per bucket, admin-set."""

    __tablename__ = "demo_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bucket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)  # used in URL /try/:slug
    access_code: Mapped[str] = mapped_column(String(4), nullable=False)   # admin-set 4-digit

    cap_team_members: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    cap_threads: Mapped[int] = mapped_column(Integer, nullable=False, default=10)      # chats / conversations
    cap_messages: Mapped[int] = mapped_column(Integer, nullable=False, default=100)    # total across bucket
    cap_files: Mapped[int] = mapped_column(Integer, nullable=False, default=1)         # visitor-uploaded files
    cap_file_size_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    cap_comebacks: Mapped[int] = mapped_column(Integer, nullable=False, default=3)     # per lead (by email)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    leads: Mapped[list["DemoLead"]] = relationship(
        "DemoLead", back_populates="demo_link", cascade="all, delete-orphan"
    )


class DemoLead(Base):
    """Each person who enters — a primary lead (via code) or an invited team member."""

    __tablename__ = "demo_leads"
    __table_args__ = (
        UniqueConstraint("demo_link_id", "email", name="demo_leads_link_email_unique"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    demo_link_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("demo_links.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_team_member: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # TRUE = came via invite link
    invited_by_lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("demo_leads.id", ondelete="SET NULL"), nullable=True
    )
    invite_token: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    invite_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    comeback_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # ++ on each successful entry
    color: Mapped[str | None] = mapped_column(Text, nullable=True)                   # avatar color for team members
    # Per-team-member visibility granted by the primary lead at invite time.
    # Primary leads default both to TRUE (they always see everything).
    can_view_threads: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    can_view_team: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    demo_link: Mapped["DemoLink"] = relationship("DemoLink", back_populates="leads")


class DemoEvent(Base):
    """Activity timeline — "what they did"."""

    __tablename__ = "demo_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    demo_link_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("demo_links.id", ondelete="CASCADE"), nullable=False, index=True
    )
    demo_lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("demo_leads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # login | message_sent | file_uploaded | team_invited | mcp_opened | tour_completed
    # | popup_shown | popup_snoozed | survey_submitted | meeting_requested | limit_hit
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class DemoSurvey(Base):
    """Feedback survey (distinct from the per-answer ``message_feedback`` table)."""

    __tablename__ = "demo_survey"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    demo_link_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("demo_links.id", ondelete="CASCADE"), nullable=False, index=True
    )
    demo_lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("demo_leads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)            # 1..5 stars
    experience: Mapped[dict | None] = mapped_column(JSONB, nullable=True)         # "how was your experience" dropdowns
    product_answers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)    # "does it help with…", "anything you wish"
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    wants_to_talk: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    talk_reason: Mapped[str | None] = mapped_column(Text, nullable=True)          # why / why not
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DemoMeetingRequest(Base):
    """"Let's talk" call requests (mirrors the enterprise_inquiries pattern)."""

    __tablename__ = "demo_meeting_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    demo_link_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("demo_links.id", ondelete="CASCADE"), nullable=False, index=True
    )
    demo_lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("demo_leads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    preferred_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")  # pending|scheduled|done|declined
    zoom_link: Mapped[str | None] = mapped_column(Text, nullable=True)            # admin pastes
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
