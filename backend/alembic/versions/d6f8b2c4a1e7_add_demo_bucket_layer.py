"""add public demo bucket layer (demo_* tables + is_demo / demo_lead_id columns)

Revision ID: d6f8b2c4a1e7
Revises: c5e7a9b1d3f0
Create Date: 2026-06-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d6f8b2c4a1e7"
down_revision: Union[str, None] = "c5e7a9b1d3f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── demo_links — the demo config wrapping one real bucket ──────────────────
    op.create_table(
        "demo_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("bucket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("access_code", sa.String(length=4), nullable=False),
        sa.Column("cap_team_members", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("cap_threads", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("cap_messages", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("cap_files", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("cap_file_size_mb", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("cap_comebacks", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("slug", name="demo_links_slug_unique"),
    )
    op.create_index("ix_demo_links_bucket_id", "demo_links", ["bucket_id"])

    # ── demo_leads — each visitor (primary lead or invited team member) ────────
    op.create_table(
        "demo_leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("demo_link_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("demo_links.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=True),
        sa.Column("is_team_member", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        # Self-referential FK: which lead invited this team member.
        sa.Column("invited_by_lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("demo_leads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("invite_token", sa.String(length=64), nullable=True),
        sa.Column("invite_token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comeback_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("color", sa.Text(), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("demo_link_id", "email", name="demo_leads_link_email_unique"),
        sa.UniqueConstraint("invite_token", name="demo_leads_invite_token_unique"),
    )
    op.create_index("ix_demo_leads_demo_link_id", "demo_leads", ["demo_link_id"])

    # ── demo_events — activity timeline ───────────────────────────────────────
    op.create_table(
        "demo_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("demo_link_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("demo_links.id", ondelete="CASCADE"), nullable=False),
        sa.Column("demo_lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("demo_leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_demo_events_demo_link_id", "demo_events", ["demo_link_id"])
    op.create_index("ix_demo_events_demo_lead_id", "demo_events", ["demo_lead_id"])
    op.create_index("ix_demo_events_created_at", "demo_events", ["created_at"])

    # ── demo_survey — feedback survey ─────────────────────────────────────────
    op.create_table(
        "demo_survey",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("demo_link_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("demo_links.id", ondelete="CASCADE"), nullable=False),
        sa.Column("demo_lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("demo_leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("experience", postgresql.JSONB(), nullable=True),
        sa.Column("product_answers", postgresql.JSONB(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("wants_to_talk", sa.Boolean(), nullable=True),
        sa.Column("talk_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_demo_survey_demo_link_id", "demo_survey", ["demo_link_id"])
    op.create_index("ix_demo_survey_demo_lead_id", "demo_survey", ["demo_lead_id"])

    # ── demo_meeting_requests — "let's talk" call requests ────────────────────
    op.create_table(
        "demo_meeting_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("demo_link_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("demo_links.id", ondelete="CASCADE"), nullable=False),
        sa.Column("demo_lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("demo_leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("preferred_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("zoom_link", sa.Text(), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_demo_meeting_requests_demo_link_id", "demo_meeting_requests", ["demo_link_id"])
    op.create_index("ix_demo_meeting_requests_demo_lead_id", "demo_meeting_requests", ["demo_lead_id"])
    op.create_index("ix_demo_meeting_requests_status", "demo_meeting_requests", ["status"])

    # ── minimal touch on existing tables ──────────────────────────────────────
    op.add_column(
        "buckets",
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "conversations",
        sa.Column("demo_lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("demo_leads.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_conversations_demo_lead_id", "conversations", ["demo_lead_id"])


def downgrade() -> None:
    op.drop_index("ix_conversations_demo_lead_id", table_name="conversations")
    op.drop_column("conversations", "demo_lead_id")
    op.drop_column("buckets", "is_demo")

    op.drop_index("ix_demo_meeting_requests_status", table_name="demo_meeting_requests")
    op.drop_index("ix_demo_meeting_requests_demo_lead_id", table_name="demo_meeting_requests")
    op.drop_index("ix_demo_meeting_requests_demo_link_id", table_name="demo_meeting_requests")
    op.drop_table("demo_meeting_requests")

    op.drop_index("ix_demo_survey_demo_lead_id", table_name="demo_survey")
    op.drop_index("ix_demo_survey_demo_link_id", table_name="demo_survey")
    op.drop_table("demo_survey")

    op.drop_index("ix_demo_events_created_at", table_name="demo_events")
    op.drop_index("ix_demo_events_demo_lead_id", table_name="demo_events")
    op.drop_index("ix_demo_events_demo_link_id", table_name="demo_events")
    op.drop_table("demo_events")

    op.drop_index("ix_demo_leads_demo_link_id", table_name="demo_leads")
    op.drop_table("demo_leads")

    op.drop_index("ix_demo_links_bucket_id", table_name="demo_links")
    op.drop_table("demo_links")
