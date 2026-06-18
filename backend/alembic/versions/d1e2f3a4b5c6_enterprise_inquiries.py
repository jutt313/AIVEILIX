"""enterprise inquiries table

Revision ID: d1e2f3a4b5c6
Revises: c8a4d1f02b34
Create Date: 2026-06-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, None] = "c8a4d1f02b34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_inquiries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=255), nullable=True),
        sa.Column("team_size", sa.String(length=100), nullable=True),
        sa.Column("doc_volume", sa.String(length=100), nullable=True),
        sa.Column("use_case", sa.Text(), nullable=True),
        sa.Column("meeting_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="new"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_enterprise_inquiries_user_id", "enterprise_inquiries", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_enterprise_inquiries_user_id", table_name="enterprise_inquiries")
    op.drop_table("enterprise_inquiries")
