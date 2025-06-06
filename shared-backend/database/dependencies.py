"""
Database dependencies for FastAPI dependency injection
Handles database session management and cleanup
"""

from contextlib import contextmanager
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator
import logging

from .connection import engine, database
from ..config import settings

logger = logging.getLogger(__name__)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session
    Automatically handles session cleanup and rollback on errors
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database operation: {e}")
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_db_session_context():
    """
    Context manager for database sessions
    Use this for operations outside of FastAPI endpoints
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error in context: {e}")
        session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database context: {e}")
        session.rollback()
        raise
    finally:
        session.close()


async def get_async_db_session():
    """
    Async database session dependency
    For use with async database operations
    """
    async with database.transaction():
        yield database


class DatabaseManager:
    """
    Database manager for handling connections and sessions
    """
    
    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal
    
    def create_session(self) -> Session:
        """Create a new database session"""
        return self.session_factory()
    
    def health_check(self) -> bool:
        """Check if database is healthy"""
        try:
            with self.create_session() as session:
                session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def async_health_check(self) -> bool:
        """Async database health check"""
        try:
            await database.fetch_one("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Async database health check failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """Get database connection information"""
        return {
            "database_url": settings.DATABASE_URL,
            "pool_size": self.engine.pool.size(),
            "checked_out": self.engine.pool.checkedout(),
            "overflow": self.engine.pool.overflow(),
            "invalidated": self.engine.pool.invalidated()
        }


# Global database manager instance
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """FastAPI dependency to get database manager"""
    return db_manager


class TransactionManager:
    """
    Context manager for handling database transactions
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.transaction = None
    
    def __enter__(self):
        self.transaction = self.session.begin()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.transaction.rollback()
            logger.error(f"Transaction rolled back due to: {exc_val}")
        else:
            self.transaction.commit()
        self.transaction = None


def with_transaction(session: Session):
    """
    Decorator/context manager for wrapping operations in transactions
    """
    return TransactionManager(session)


async def execute_in_transaction(operation, *args, **kwargs):
    """
    Execute an operation within a database transaction
    """
    async with database.transaction():
        return await operation(*args, **kwargs)


def create_tables():
    """
    Create all database tables
    Should only be run during initialization
    """
    try:
        from .models import metadata
        metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables
    Use with caution - only for development/testing
    """
    try:
        from .models import metadata
        metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def reset_database():
    """
    Reset database by dropping and recreating all tables
    Use with extreme caution - only for development
    """
    if settings.ENVIRONMENT == "production":
        raise ValueError("Cannot reset database in production environment")
    
    logger.warning("Resetting database...")
    drop_tables()
    create_tables()
    logger.info("Database reset completed")


class DatabaseInitializer:
    """
    Handles database initialization and setup
    """
    
    @staticmethod
    def initialize():
        """Initialize database with required data"""
        try:
            # Create tables
            create_tables()
            
            # Insert default data
            DatabaseInitializer._insert_default_data()
            
            logger.info("Database initialization completed")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    @staticmethod
    def _insert_default_data():
        """Insert default system data"""
        with get_db_session_context() as session:
            from .models import SystemSettings, AdminUser
            from ..auth.dependencies import hash_password
            import uuid
            
            # Check if admin user exists
            admin_exists = session.query(AdminUser).first()
            
            if not admin_exists:
                # Create default admin user
                default_admin = AdminUser(
                    id=uuid.uuid4(),
                    email="admin@openhealth.com",
                    name="System Administrator",
                    role="super_admin",
                    permissions=["super_admin"]
                )
                session.add(default_admin)
                logger.info("Default admin user created")
            
            # Insert default system settings
            default_settings = [
                {
                    "key": "system_initialized",
                    "value": {"initialized": True, "version": "1.0.0"},
                    "description": "System initialization status"
                },
                {
                    "key": "ai_models",
                    "value": {
                        "default_model": settings.DEFAULT_AI_MODEL,
                        "embedding_model": settings.EMBEDDING_MODEL,
                        "max_tokens": settings.MAX_TOKENS,
                        "temperature": settings.TEMPERATURE
                    },
                    "description": "AI model configuration"
                },
                {
                    "key": "venture_scoring",
                    "value": {
                        "market_opportunity_weight": 0.3,
                        "team_strength_weight": 0.25,
                        "technology_innovation_weight": 0.2,
                        "business_model_weight": 0.15,
                        "execution_capability_weight": 0.1
                    },
                    "description": "Venture scoring weights"
                }
            ]
            
            for setting_data in default_settings:
                existing = session.query(SystemSettings).filter(
                    SystemSettings.key == setting_data["key"]
                ).first()
                
                if not existing:
                    setting = SystemSettings(
                        key=setting_data["key"],
                        value=setting_data["value"],
                        description=setting_data["description"]
                    )
                    session.add(setting)
            
            session.commit()
            logger.info("Default system settings inserted")


# Initialize database on module import if needed
def ensure_database_initialized():
    """Ensure database is initialized"""
    try:
        if settings.ENVIRONMENT in ["development", "testing"]:
            # Check if database is initialized
            with get_db_session_context() as session:
                from .models import SystemSettings
                
                initialized = session.query(SystemSettings).filter(
                    SystemSettings.key == "system_initialized"
                ).first()
                
                if not initialized:
                    logger.info("Database not initialized, initializing now...")
                    DatabaseInitializer.initialize()
                    
    except Exception as e:
        logger.warning(f"Could not check database initialization: {e}")