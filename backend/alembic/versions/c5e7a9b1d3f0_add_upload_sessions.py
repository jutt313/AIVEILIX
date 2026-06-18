"""add upload_sessions table (direct-to-R2 uploads)

Revision ID: c5e7a9b1d3f0
Revises: a7b8c9d0e1f2
Create Date: 2026-06-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c5e7a9b1d3f0"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


mode_enum = sa.Enum("single", "multipart", name="upload_session_mode")
status_enum = sa.Enum(
    "initiated", "uploaded", "completed", "aborted", "failed",
    name="upload_session_status",
)


def upgrade() -> None:
    op.create_table(
        "upload_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        # file_id is NOT a FK: the files row is only created on completion.
        sa.Column("file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bucket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("content_type", sa.Text(), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("r2_key", sa.Text(), nullable=False),
        sa.Column("mode", mode_enum, nullable=False),
        sa.Column("r2_upload_id", sa.Text(), nullable=True),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_upload_sessions_file_id", "upload_sessions", ["file_id"], unique=True)
    op.create_index("ix_upload_sessions_bucket_id", "upload_sessions", ["bucket_id"])
    op.create_index("ix_upload_sessions_user_id", "upload_sessions", ["user_id"])
    op.create_index("ix_upload_sessions_status", "upload_sessions", ["status"])


def downgrade() -> None:
    op.drop_index("ix_upload_sessions_status", table_name="upload_sessions")
    op.drop_index("ix_upload_sessions_user_id", table_name="upload_sessions")
    op.drop_index("ix_upload_sessions_bucket_id", table_name="upload_sessions")
    op.drop_index("ix_upload_sessions_file_id", table_name="upload_sessions")
    op.drop_table("upload_sessions")
    status_enum.drop(op.get_bind(), checkfirst=True)
    mode_enum.drop(op.get_bind(), checkfirst=True)
