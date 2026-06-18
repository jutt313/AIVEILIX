"""add message_feedback and agent_written columns

Revision ID: c4d6d2535e48
Revises:
Create Date: 2026-04-04 11:48:22.437322

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "c4d6d2535e48"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


feedback_rating = postgresql.ENUM("like", "dislike", name="feedback_rating", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    feedback_rating.create(bind, checkfirst=True)

    op.create_table(
        "message_feedback",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("message_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("rating", feedback_rating, nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_message_feedback_message_id"), "message_feedback", ["message_id"], unique=False)
    op.create_index(op.f("ix_message_feedback_user_id"), "message_feedback", ["user_id"], unique=False)

    op.add_column(
        "files",
        sa.Column("is_agent_written", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.alter_column("files", "is_agent_written", server_default=None)

    op.add_column("messages", sa.Column("agent_wrote_file_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_messages_agent_wrote_file_id_files",
        "messages",
        "files",
        ["agent_wrote_file_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_messages_agent_wrote_file_id_files", "messages", type_="foreignkey")
    op.drop_column("messages", "agent_wrote_file_id")

    op.drop_column("files", "is_agent_written")

    op.drop_index(op.f("ix_message_feedback_user_id"), table_name="message_feedback")
    op.drop_index(op.f("ix_message_feedback_message_id"), table_name="message_feedback")
    op.drop_table("message_feedback")

    feedback_rating.drop(op.get_bind(), checkfirst=True)
