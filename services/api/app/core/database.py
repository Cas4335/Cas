"""
SQLAlchemy database engine and session management.
"""

from typing import Generator, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, scoped_session

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Lazy initialization — engine is created on first use, not at import time.
# This allows tests to override the database URL before the engine is created.
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> sessionmaker:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


# Keep a module-level reference for backward compatibility
# (Alembic's env.py uses `engine` directly)
@property
def engine(self):
    return get_engine()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a database session and closes it after use."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
