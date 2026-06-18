"""add conversations is_pinned

Revision ID: 12ea92355c52
Revises: 9af1ec882be9
Create Date: 2026-05-12 21:22:05.306855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12ea92355c52'
down_revision: Union[str, None] = '9af1ec882be9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column("is_pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.alter_column("conversations", "is_pinned", server_default=None)


def downgrade() -> None:
    op.drop_column("conversations", "is_pinned")
