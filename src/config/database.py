from collections.abc import AsyncGenerator, Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from .settings import settings


# Sync engine (for Alembic migrations)
sync_engine = create_engine(settings.database_url)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async engine (for FastAPI/GraphQL)
async_engine = create_async_engine(
    settings.database_url.replace("postgresql+psycopg://", "postgresql+psycopg://"),
    echo=False,
    future=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Dependency for sync sessions (Alembic, testing)
def get_sync_db() -> Generator[Session]:
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency for async sessions (FastAPI, GraphQL)
async def get_async_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@contextmanager
def db_scope() -> Generator[Session]:
    """
    Helps to manage database operations outside of FastAPI.
    Ensures that a group of operations are treated as a single transaction.
    Easy for setup and teardown of sessions.
    """
    db = SyncSessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.expire_on_commit = False
        db.close()
