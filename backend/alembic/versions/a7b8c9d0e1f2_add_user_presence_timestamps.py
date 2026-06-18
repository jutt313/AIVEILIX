"""add user presence timestamps (last_login_at, last_seen_at)

Revision ID: a7b8c9d0e1f2
Revises: ea4f72c0d9b1
Create Date: 2026-06-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = 'ea4f72c0d9b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_users_last_seen_at"), "users", ["last_seen_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_last_seen_at"), table_name="users")
    op.drop_column("users", "last_seen_at")
    op.drop_column("users", "last_login_at")
