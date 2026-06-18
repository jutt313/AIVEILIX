"""merge enterprise_inquiries + limit_requests heads

Revision ID: 3b8c2e3938c4
Revises: d1e2f3a4b5c6, d9e0f1a2b3c4
Create Date: 2026-06-13 14:22:19.754023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b8c2e3938c4'
down_revision: Union[str, None] = ('d1e2f3a4b5c6', 'd9e0f1a2b3c4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
