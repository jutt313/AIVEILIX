from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def get_db() -> AsyncSession:
    async with db_session() as session:
        yield session


async def check_postgres_connection() -> dict[str, object]:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT current_database() AS db, current_user AS user_name, version() AS version"))
        row = result.mappings().one()
        return {
            "status": "ok",
            "database": row["db"],
            "user": row["user_name"],
            "version": row["version"].split(",")[0],
        }
