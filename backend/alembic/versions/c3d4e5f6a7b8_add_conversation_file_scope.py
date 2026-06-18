"""add conversation_file_scope

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-24 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversation_file_scope",
        sa.Column("conversation_id", sa.dialects.postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_id", sa.dialects.postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
        sa.PrimaryKeyConstraint("conversation_id", "file_id"),
    )
    op.create_index(
        "ix_conversation_file_scope_conv",
        "conversation_file_scope",
        ["conversation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_conversation_file_scope_conv", table_name="conversation_file_scope")
    op.drop_table("conversation_file_scope")
