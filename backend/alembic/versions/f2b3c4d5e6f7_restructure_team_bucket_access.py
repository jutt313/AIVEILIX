"""restructure team_bucket_access with granular boolean permissions

Revision ID: f2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-06-10 12:05:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f2b3c4d5e6f7"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PERMISSION_COLUMNS = [
    ("can_view_threads", True),
    ("can_create_threads", False),
    ("can_read_existing_threads", False),
    ("can_see_other_members", False),
    ("can_upload_files", False),
    ("can_download_files", False),
    ("can_delete_files", False),
    ("can_use_mcp", False),
    ("can_use_web_search", False),
]


def upgrade() -> None:
    for col_name, default in PERMISSION_COLUMNS:
        op.add_column(
            "team_bucket_access",
            sa.Column(
                col_name,
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true" if default else "false"),
            ),
        )

    op.add_column(
        "team_bucket_access",
        sa.Column("granted_by_user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "team_bucket_access",
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_foreign_key(
        "team_bucket_access_granted_by_fk",
        "team_bucket_access",
        "users",
        ["granted_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.drop_column("team_bucket_access", "permission")
    op.execute("DROP TYPE IF EXISTS team_bucket_permission")


def downgrade() -> None:
    op.execute("CREATE TYPE team_bucket_permission AS ENUM ('read', 'write', 'admin')")
    op.add_column(
        "team_bucket_access",
        sa.Column(
            "permission",
            sa.Enum("read", "write", "admin", name="team_bucket_permission", create_type=False),
            nullable=False,
            server_default="read",
        ),
    )

    op.drop_constraint(
        "team_bucket_access_granted_by_fk",
        "team_bucket_access",
        type_="foreignkey",
    )
    op.drop_column("team_bucket_access", "granted_at")
    op.drop_column("team_bucket_access", "granted_by_user_id")

    for col_name, _ in reversed(PERMISSION_COLUMNS):
        op.drop_column("team_bucket_access", col_name)
