"""add mcp token tables

Revision ID: 9af1ec882be9
Revises: c4d6d2535e48
Create Date: 2026-04-06 09:22:55.188176

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9af1ec882be9'
down_revision: Union[str, None] = 'c4d6d2535e48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bucket_mcp_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("bucket_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("allowed_tools", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("allowed_origins", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["bucket_id"], ["buckets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index(op.f("ix_bucket_mcp_tokens_bucket_id"), "bucket_mcp_tokens", ["bucket_id"], unique=False)
    op.create_index(op.f("ix_bucket_mcp_tokens_user_id"), "bucket_mcp_tokens", ["user_id"], unique=False)

    op.create_table(
        "mcp_access_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("token_id", sa.UUID(), nullable=False),
        sa.Column("bucket_id", sa.UUID(), nullable=False),
        sa.Column("tool", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("origin", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["token_id"], ["bucket_mcp_tokens.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mcp_access_logs_bucket_id"), "mcp_access_logs", ["bucket_id"], unique=False)
    op.create_index(op.f("ix_mcp_access_logs_created_at"), "mcp_access_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_mcp_access_logs_token_id"), "mcp_access_logs", ["token_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_mcp_access_logs_token_id"), table_name="mcp_access_logs")
    op.drop_index(op.f("ix_mcp_access_logs_created_at"), table_name="mcp_access_logs")
    op.drop_index(op.f("ix_mcp_access_logs_bucket_id"), table_name="mcp_access_logs")
    op.drop_table("mcp_access_logs")

    op.drop_index(op.f("ix_bucket_mcp_tokens_user_id"), table_name="bucket_mcp_tokens")
    op.drop_index(op.f("ix_bucket_mcp_tokens_bucket_id"), table_name="bucket_mcp_tokens")
    op.drop_table("bucket_mcp_tokens")
