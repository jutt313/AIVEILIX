"""add per-lead view permissions for the demo team layer

Revision ID: e8a1c0d4f7b2
Revises: d6f8b2c4a1e7
Create Date: 2026-06-21

Adds:
  * demo_leads.can_view_threads / can_view_team — per-team-member visibility
    granted by the owner (primary lead) at invite time. The owner (the first
    visitor who entered the code) always sees everything; existing primary-lead
    rows are backfilled to TRUE, invited team members default to FALSE.
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

    # Backfill: the owner (is_team_member = false) always sees everything.
    op.execute(
        "UPDATE demo_leads SET can_view_threads = true, can_view_team = true "
        "WHERE is_team_member = false"
    )


def downgrade() -> None:
    op.drop_column("demo_leads", "can_view_team")
    op.drop_column("demo_leads", "can_view_threads")
