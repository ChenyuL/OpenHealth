"""
Database connection configuration for OpenHealth
"""

from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import settings

# Create database instance
database = Database(settings.DATABASE_URL)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create metadata instance
metadata = MetaData()

# Create declarative base
Base = declarative_base(metadata=metadata)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_database():
    """Get database instance for dependency injection"""
    return database


def get_db():
    """Get database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
