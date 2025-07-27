"""
Database connection and session management.

This module provides database connection setup, session management,
and utility functions for the AI Assistant Platform.
"""

from collections.abc import Generator

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

from .config import get_settings

# Create database engine
engine = create_engine(
    get_settings().database_url,
    poolclass=QueuePool,
    pool_size=get_settings().database_pool_size,
    max_overflow=get_settings().database_max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=get_settings().debug,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Create declarative base using SQLAlchemy 2.0 syntax
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.

    Yields:
        Session: Database session

    Example:
        ```python
        db = next(get_db())
        try:
            # Use database session
            pass
        finally:
            db.close()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_default_admin_user():
    """Create default admin user if none exist."""
    logger.info("Admin user creation should be done via CLI tool for security")


def create_default_assistant():
    """Create a default assistant if none exists."""
    try:
        from backend.app.models.assistant import Assistant, AssistantStatus
        from backend.app.models.user import User

        # Get database session
        db = next(get_db())

        # Check if any assistants exist
        existing_assistant = db.query(Assistant).first()
        if existing_assistant:
            logger.info("Assistants already exist, skipping default assistant creation")
            return

        # Get or create admin user
        admin_user = db.query(User).filter(User.role == "admin").first()
        if not admin_user:
            logger.info("No admin user found, creating default admin user")
            admin_user = create_default_admin_user()
            if not admin_user:
                logger.warning(
                    "Failed to create admin user, cannot create default assistant"
                )
                return

        # Create default assistant
        default_assistant = Assistant(
            creator_id=admin_user.id,
            name="Default Assistant",
            description="A general-purpose AI assistant for everyday tasks",
            system_prompt="You are a helpful AI assistant that can help with various tasks including answering questions, writing content, and solving problems.",
            model="gpt-4",
            temperature="0.7",
            max_tokens="4096",
            status=AssistantStatus.ACTIVE,
            is_public=True,
            is_template=False,
            category="general",
            tags=["default", "general", "helpful"],
            tools_config=[],
            tools_enabled=True,
        )

        db.add(default_assistant)
        db.commit()
        db.refresh(default_assistant)

        logger.info(f"Created default assistant: {default_assistant.id}")

    except Exception as e:
        logger.error(f"Failed to create default assistant: {e}")
        if "db" in locals():
            db.rollback()


def init_db() -> None:
    """Initialize database tables."""
    try:
        # Import all models to ensure they are registered
        from backend.app.models import Base

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Create default admin user and assistant
        create_default_admin_user()
        create_default_assistant()

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def check_db_connection() -> bool:
    """
    Check database connection.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_db_info() -> dict:
    """
    Get database information.

    Returns:
        dict: Database information including connection status and pool stats
    """
    try:
        pool = engine.pool
        return {
            "status": "connected" if check_db_connection() else "disconnected",
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
        }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {"status": "error", "error": str(e)}
