"""rename pro subscription plan to individual

Revision ID: ea4f72c0d9b1
Revises: 3b8c2e3938c4
Create Date: 2026-06-13
"""

from typing import Sequence, Union

from alembic import op

revision: str = "ea4f72c0d9b1"
down_revision: Union[str, Sequence[str], None] = "3b8c2e3938c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'subscription_plan' AND e.enumlabel = 'pro'
              ) THEN
                IF EXISTS (
                  SELECT 1
                  FROM pg_type t
                  JOIN pg_enum e ON t.oid = e.enumtypid
                  WHERE t.typname = 'subscription_plan' AND e.enumlabel = 'individual'
                ) THEN
                  UPDATE subscriptions SET plan = 'individual' WHERE plan = 'pro';
                ELSE
                  ALTER TYPE subscription_plan RENAME VALUE 'pro' TO 'individual';
                END IF;
              END IF;
            END $$;
            """
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname = 'subscription_plan' AND e.enumlabel = 'individual'
              ) THEN
                IF EXISTS (
                  SELECT 1
                  FROM pg_type t
                  JOIN pg_enum e ON t.oid = e.enumtypid
                  WHERE t.typname = 'subscription_plan' AND e.enumlabel = 'pro'
                ) THEN
                  UPDATE subscriptions SET plan = 'pro' WHERE plan = 'individual';
                ELSE
                  ALTER TYPE subscription_plan RENAME VALUE 'individual' TO 'pro';
                END IF;
              END IF;
            END $$;
            """
        )
