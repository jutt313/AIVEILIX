"""add demo upload page and visual caps

Revision ID: f9b2c3d4e6a8
Revises: e8a1c0d4f7b2
Create Date: 2026-06-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f9b2c3d4e6a8"
down_revision: Union[str, None] = "e8a1c0d4f7b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "demo_links",
        sa.Column("cap_file_pages", sa.Integer(), nullable=False, server_default="100"),
    )
    op.add_column(
        "demo_links",
        sa.Column("cap_file_visuals", sa.Integer(), nullable=False, server_default="100"),
    )


def downgrade() -> None:
    op.drop_column("demo_links", "cap_file_visuals")
    op.drop_column("demo_links", "cap_file_pages")
