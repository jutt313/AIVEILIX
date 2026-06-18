"""add file asset manifest columns

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-29

Adds image_count + section_outline to files, persisted at ingest so the
agent can answer structural questions (how many images, what sections,
which page does X start on) without going through vector search.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "files",
        sa.Column("image_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "files",
        sa.Column(
            "section_outline",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("files", "section_outline")
    op.drop_column("files", "image_count")
