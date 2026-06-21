"""add demo primary-lead fields + per-lead view permissions

Revision ID: e8a1c0d4f7b2
Revises: d6f8b2c4a1e7
Create Date: 2026-06-21

Adds:
  * demo_links.primary_lead_name / primary_lead_email / primary_lead_role
    so admin captures the customer's identity when creating the bucket — the
    /try/:slug entry page can then skip the "tell us who you are" step.
  * demo_leads.can_view_threads / can_view_team — per-team-member visibility
    granted by the primary lead at invite time. Primary leads default to TRUE
    for both (they always see everything). Existing rows: primary leads get
    TRUE, team members get FALSE (safe default).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e8a1c0d4f7b2"
down_revision: Union[str, None] = "d6f8b2c4a1e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "demo_links",
        sa.Column("primary_lead_name", sa.Text(), nullable=True),
    )
    op.add_column(
        "demo_links",
        sa.Column("primary_lead_email", sa.Text(), nullable=True),
    )
    op.add_column(
        "demo_links",
        sa.Column("primary_lead_role", sa.Text(), nullable=True),
    )

    op.add_column(
        "demo_leads",
        sa.Column(
            "can_view_threads",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "demo_leads",
        sa.Column(
            "can_view_team",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # Backfill: primary leads (is_team_member = false) always see everything.
    op.execute(
        "UPDATE demo_leads SET can_view_threads = true, can_view_team = true "
        "WHERE is_team_member = false"
    )


def downgrade() -> None:
    op.drop_column("demo_leads", "can_view_team")
    op.drop_column("demo_leads", "can_view_threads")
    op.drop_column("demo_links", "primary_lead_role")
    op.drop_column("demo_links", "primary_lead_email")
    op.drop_column("demo_links", "primary_lead_name")
