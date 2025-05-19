from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
from app.core.config import settings

# Create SQLite engine
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{settings.DATABASE_NAME}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# Store the current database engine (useful for testing)
_engine = engine


# Dependency for database session
def get_db() -> Generator:
    """
    Dependency function that provides a SQLAlchemy session.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_engine():
    """Get the current database engine."""
    return _engine


def set_engine(new_engine):
    """Set a new database engine (useful for testing)."""
    global _engine, SessionLocal
    _engine = new_engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
