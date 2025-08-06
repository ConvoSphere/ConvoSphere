"""
Database connection and session management.

This module provides database connection setup, session management,
and utility functions for the AI Assistant Platform.
"""

from collections.abc import Generator
from typing import Any

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


def create_default_admin_user() -> Any | None:
    """Create and return a fallback admin user (development only)."""
    try:
        import os
        from datetime import UTC, datetime
        from uuid import uuid4

        from backend.app.core.security import get_password_hash
        from backend.app.models.user import User

        # Only create default admin if explicitly requested
        if os.getenv("CREATE_DEFAULT_ADMIN", "false").lower() != "true":
            logger.info("CREATE_DEFAULT_ADMIN not set to true, skipping default admin creation")
            return None

        db = next(get_db())

        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            logger.info("Admin user already exists, skipping default admin creation")
            return existing_admin

        # Get admin credentials from environment variables
        admin_email = os.getenv("DEFAULT_ADMIN_EMAIL")
        admin_username = os.getenv("DEFAULT_ADMIN_USERNAME")
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")

        if not all([admin_email, admin_username, admin_password]):
            logger.warning(
                "DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_USERNAME, and DEFAULT_ADMIN_PASSWORD "
                "must be set to create default admin user"
            )
            return None

        logger.info(f"Creating default admin user: {admin_email}")

        admin_user = User(
            id=uuid4(),
            email=admin_email,
            username=admin_username,
            hashed_password=get_password_hash(admin_password),
            role="admin",
            is_verified=True,
            language="en",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        logger.info(f"Successfully created default admin user: {admin_user.id}")
        return admin_user
    except Exception as exc:  # pragma: no cover
        logger.error(f"Failed to create default admin user: {exc}")
        if "db" in locals():
            db.rollback()
        return None


def create_default_assistant() -> None:
    """Create a default assistant if explicitly requested."""
    try:
        import os

        from backend.app.models.assistant import Assistant, AssistantStatus
        from backend.app.models.user import User

        # Only create default assistant if explicitly requested
        if os.getenv("CREATE_DEFAULT_ASSISTANT", "false").lower() != "true":
            logger.info("CREATE_DEFAULT_ASSISTANT not set to true, skipping default assistant creation")
            return

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
            logger.warning(
                "No admin user found, cannot create default assistant. "
                "Please create an admin user first or set CREATE_DEFAULT_ADMIN=true"
            )
            return

        # Get assistant configuration from environment variables
        assistant_name = os.getenv("DEFAULT_ASSISTANT_NAME", "Default Assistant")
        assistant_description = os.getenv(
            "DEFAULT_ASSISTANT_DESCRIPTION",
            "A general-purpose AI assistant for everyday tasks"
        )
        assistant_system_prompt = os.getenv(
            "DEFAULT_ASSISTANT_SYSTEM_PROMPT",
            "You are a helpful AI assistant that can help with various tasks including answering questions, writing content, and solving problems."
        )
        assistant_model = os.getenv("DEFAULT_ASSISTANT_MODEL", "gpt-4")

        # Create default assistant
        default_assistant = Assistant(
            creator_id=admin_user.id,
            name=assistant_name,
            description=assistant_description,
            system_prompt=assistant_system_prompt,
            model=assistant_model,
            temperature=0.7,
            max_tokens=4096,
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


def get_db_info() -> dict[str, Any]:
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
