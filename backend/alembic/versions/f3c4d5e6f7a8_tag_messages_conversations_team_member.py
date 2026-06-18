"""tag messages and conversations with sender team_member

Revision ID: f3c4d5e6f7a8
Revises: f2b3c4d5e6f7
Create Date: 2026-06-10 12:10:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f3c4d5e6f7a8"
down_revision: Union[str, None] = "f2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "messages",
        sa.Column(
            "sender_team_member_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_messages_sender_team_member_id",
        "messages",
        "team_members",
        ["sender_team_member_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "messages_sender_team_member_id_idx",
        "messages",
        ["sender_team_member_id"],
    )

    op.add_column(
        "conversations",
        sa.Column(
            "created_by_team_member_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_conversations_created_by_team_member_id",
        "conversations",
        "team_members",
        ["created_by_team_member_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "conversations_created_by_team_member_id_idx",
        "conversations",
        ["created_by_team_member_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "conversations_created_by_team_member_id_idx",
        table_name="conversations",
    )
    op.drop_constraint(
        "fk_conversations_created_by_team_member_id",
        "conversations",
        type_="foreignkey",
    )
    op.drop_column("conversations", "created_by_team_member_id")

    op.drop_index(
        "messages_sender_team_member_id_idx",
        table_name="messages",
    )
    op.drop_constraint(
        "fk_messages_sender_team_member_id",
        "messages",
        type_="foreignkey",
    )
    op.drop_column("messages", "sender_team_member_id")
