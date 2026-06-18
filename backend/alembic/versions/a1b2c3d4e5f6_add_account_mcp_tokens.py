"""add account mcp tokens

Revision ID: a1b2c3d4e5f6
Revises: 12ea92355c52
Create Date: 2026-05-22 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '12ea92355c52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "account_mcp_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("bucket_mode", sa.String(length=20), nullable=False, server_default=sa.text("'all'")),
        sa.Column(
            "allowed_bucket_ids",
            postgresql.ARRAY(sa.UUID()),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index(op.f("ix_account_mcp_tokens_user_id"), "account_mcp_tokens", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_account_mcp_tokens_user_id"), table_name="account_mcp_tokens")
    op.drop_table("account_mcp_tokens")
