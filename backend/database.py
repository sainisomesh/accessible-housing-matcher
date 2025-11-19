"""Database setup for HousingMatcher.

This module configures a SQLAlchemy engine and session factory for
interacting with a SQLite database. It exposes a `Base` object for
declarative models and a `get_db` dependency function that yields a
database session to FastAPI endpoints.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database stored locally. When deploying, you may swap this
# connection string for a cloud-hosted database such as PostgreSQL.
SQLALCHEMY_DATABASE_URL = "sqlite:///./housingmatcher.db"

# The `connect_args` parameter is required only for SQLite. It ensures
# that the database operates correctly in a multi-threaded FastAPI
# environment.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class and a Base class for models.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Yield a new database session for a request and close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()