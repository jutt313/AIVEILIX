"""add 'team' value to subscription_plan enum

Revision ID: b7f3a1c92e10
Revises: f4d5e6f7a8b9
Create Date: 2026-06-12

Adds the self-serve $49 'team' plan to the subscription_plan enum
(previously: free, pro, business).
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b7f3a1c92e10"
down_revision: Union[str, None] = "f4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ADD VALUE cannot run inside a transaction block on older Postgres; use autocommit.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE subscription_plan ADD VALUE IF NOT EXISTS 'team'")


def downgrade() -> None:
    # Postgres cannot drop an enum value; 'team' is left in place (harmless).
    pass
