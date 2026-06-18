"""extend team_members with invite fields

Revision ID: f1a2b3c4d5e6
Revises: e5f6a7b8c9d0
Create Date: 2026-06-10 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "team_members",
        "member_user_id",
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=True,
    )

    op.add_column(
        "team_members",
        sa.Column("display_name", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "team_members",
        sa.Column("display_color", sa.String(length=7), nullable=True),
    )
    op.add_column(
        "team_members",
        sa.Column("invite_email", sa.Text(), nullable=True),
    )
    op.add_column(
        "team_members",
        sa.Column("invite_token", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "team_members",
        sa.Column("invite_token_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "team_members",
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "team_members",
        sa.Column("invited_by_user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "team_members",
        sa.Column("invite_note", sa.Text(), nullable=True),
    )

    op.create_foreign_key(
        "team_members_invited_by_fk",
        "team_members",
        "users",
        ["invited_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "team_members_invite_token_idx",
        "team_members",
        ["invite_token"],
        unique=True,
    )
    op.create_index(
        "team_members_owner_status_idx",
        "team_members",
        ["owner_user_id", "status"],
    )

    op.execute(
        """
        CREATE UNIQUE INDEX team_members_owner_email_pending_idx
        ON team_members (owner_user_id, lower(invite_email))
        WHERE status = 'pending' AND invite_email IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS team_members_owner_email_pending_idx")
    op.drop_index("team_members_owner_status_idx", table_name="team_members")
    op.drop_index("team_members_invite_token_idx", table_name="team_members")

    op.drop_constraint("team_members_invited_by_fk", "team_members", type_="foreignkey")

    op.drop_column("team_members", "invite_note")
    op.drop_column("team_members", "invited_by_user_id")
    op.drop_column("team_members", "accepted_at")
    op.drop_column("team_members", "invite_token_expires_at")
    op.drop_column("team_members", "invite_token")
    op.drop_column("team_members", "invite_email")
    op.drop_column("team_members", "display_color")
    op.drop_column("team_members", "display_name")

    op.alter_column(
        "team_members",
        "member_user_id",
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=False,
    )
