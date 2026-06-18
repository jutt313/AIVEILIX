"""simplify team_bucket_access permissions: history_scope + drop redundant flags

Revision ID: f4d5e6f7a8b9
Revises: f3c4d5e6f7a8
Create Date: 2026-06-10 13:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f4d5e6f7a8b9"
down_revision: Union[str, None] = "f3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add history_scope enum column.
    op.execute("CREATE TYPE team_history_scope AS ENUM ('from_now', 'all')")
    op.add_column(
        "team_bucket_access",
        sa.Column(
            "history_scope",
            sa.Enum("from_now", "all", name="team_history_scope", create_type=False),
            nullable=False,
            server_default="from_now",
        ),
    )

    # Migrate data: any row that previously had can_read_existing_threads = true
    # becomes scope='all' so we don't silently change visibility for existing grants.
    op.execute(
        "UPDATE team_bucket_access "
        "SET history_scope = 'all' "
        "WHERE can_read_existing_threads = TRUE"
    )

    # Drop the four now-redundant boolean columns.
    op.drop_column("team_bucket_access", "can_view_threads")
    op.drop_column("team_bucket_access", "can_create_threads")
    op.drop_column("team_bucket_access", "can_read_existing_threads")
    op.drop_column("team_bucket_access", "can_use_web_search")


def downgrade() -> None:
    op.add_column(
        "team_bucket_access",
        sa.Column(
            "can_view_threads",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "team_bucket_access",
        sa.Column(
            "can_create_threads",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "team_bucket_access",
        sa.Column(
            "can_read_existing_threads",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "team_bucket_access",
        sa.Column(
            "can_use_web_search",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # Backfill from history_scope so the downgrade is non-lossy.
    op.execute(
        "UPDATE team_bucket_access "
        "SET can_read_existing_threads = TRUE "
        "WHERE history_scope = 'all'"
    )

    op.drop_column("team_bucket_access", "history_scope")
    op.execute("DROP TYPE IF EXISTS team_history_scope")
