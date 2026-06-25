"""add processing_tier to buckets and files

Revision ID: a7c1e9d3b5f2
Revises: f9b2c3d4e6a8
Create Date: 2026-06-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7c1e9d3b5f2"
down_revision: Union[str, None] = "f9b2c3d4e6a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "buckets",
        sa.Column("processing_tier", sa.String(length=8), nullable=False, server_default="full"),
    )
    op.add_column(
        "files",
        sa.Column("processing_tier", sa.String(length=8), nullable=False, server_default="full"),
    )


def downgrade() -> None:
    op.drop_column("files", "processing_tier")
    op.drop_column("buckets", "processing_tier")
