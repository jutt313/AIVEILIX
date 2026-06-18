"""add limit increase requests

Revision ID: d9e0f1a2b3c4
Revises: c8a4d1f02b34
Create Date: 2026-06-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "d9e0f1a2b3c4"
down_revision: Union[str, None] = "c8a4d1f02b34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE limit_increase_request_status AS ENUM ('pending', 'approved', 'rejected');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END
        $$;
        """
    )
    op.create_table(
        "limit_increase_requests",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "owner_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "requester_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("requester_email", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "approved",
                "rejected",
                name="limit_increase_request_status",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("current_plan", sa.String(length=50), nullable=True),
        sa.Column(
            "requested_limits",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "current_usage",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("trigger_message", sa.Text(), nullable=True),
        sa.Column("user_note", sa.Text(), nullable=True),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column(
            "admin_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("applied_limits", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_limit_increase_requests_owner_status",
        "limit_increase_requests",
        ["owner_user_id", "status"],
    )
    op.create_index(
        "ix_limit_increase_requests_created_at",
        "limit_increase_requests",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_limit_increase_requests_created_at", table_name="limit_increase_requests")
    op.drop_index("ix_limit_increase_requests_owner_status", table_name="limit_increase_requests")
    op.drop_table("limit_increase_requests")
    op.execute("DROP TYPE IF EXISTS limit_increase_request_status")
