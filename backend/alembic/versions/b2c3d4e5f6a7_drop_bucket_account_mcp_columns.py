"""drop unused bucket account mcp columns

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-22 01:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("buckets", "account_mcp_url")
    op.drop_column("buckets", "account_mcp_token")


def downgrade() -> None:
    op.add_column("buckets", sa.Column("account_mcp_token", sa.Text(), nullable=True))
    op.add_column("buckets", sa.Column("account_mcp_url", sa.Text(), nullable=True))
