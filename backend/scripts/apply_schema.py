import asyncio
import os
import re
from pathlib import Path

import asyncpg
from alembic import command
from alembic.config import Config


BACKEND_ROOT = Path(__file__).resolve().parents[1]
POSTGRES_MIGRATIONS = BACKEND_ROOT / "database" / "postgres" / "migrations"
INITIAL_SCHEMA = POSTGRES_MIGRATIONS / "2026-04-01_initial_schema.sql"
ONBOARDING_SCHEMA = POSTGRES_MIGRATIONS / "2026-04-01_add_onboarding_to_profiles.sql"


def _database_url_for_asyncpg() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")
    return re.sub(r"^postgresql\+[^:]+://", "postgresql://", database_url, count=1)


async def _apply_sql_baseline() -> None:
    conn = await asyncpg.connect(dsn=_database_url_for_asyncpg())
    try:
        users_exists = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = 'users'
            )
            """
        )
        if users_exists:
            print("Initial schema already applied; public.users exists.")
        else:
            print("Applying initial PostgreSQL schema...")
            await conn.execute(INITIAL_SCHEMA.read_text())

        print("Applying onboarding schema patch...")
        await conn.execute(ONBOARDING_SCHEMA.read_text())
    finally:
        await conn.close()


def _run_alembic() -> None:
    print("Running Alembic migrations...")
    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    command.upgrade(cfg, "head")


def main() -> None:
    asyncio.run(_apply_sql_baseline())
    _run_alembic()
    print("PostgreSQL schema is up to date.")


if __name__ == "__main__":
    main()
