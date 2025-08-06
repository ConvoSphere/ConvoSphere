"""
Base model with cross-database compatibility.

This module provides base classes and utilities for database-agnostic models
that work with both PostgreSQL and SQLite.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from backend.app.core.config import get_settings

# Create declarative base
Base = declarative_base()


def get_uuid_column() -> Any:
    """
    Get appropriate UUID column type based on database.

    Returns:
        SQLAlchemy column type that works with both PostgreSQL and SQLite
    """
    engine_url = get_settings().database_url

    if "postgresql" in engine_url:
        return PostgresUUID(as_uuid=True)
    # SQLite fallback - use String with UUID validation
    return String(36)


def get_json_column() -> Any:
    """
    Get appropriate JSON column type based on database.

    Returns:
        SQLAlchemy column type that works with both PostgreSQL and SQLite
    """
    engine_url = get_settings().database_url

    if "postgresql" in engine_url:
        return JSONB
    # SQLite fallback - use JSON (stored as TEXT)
    from sqlalchemy import JSON

    return JSON


class TimestampMixin:
    """Mixin for adding timestamp fields to models."""

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class UUIDMixin:
    """Mixin for adding UUID primary key to models."""

    id = Column(get_uuid_column(), primary_key=True, default=uuid.uuid4)


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Base model with UUID primary key and timestamps.

    This model provides:
    - UUID primary key (cross-database compatible)
    - Created/updated timestamps
    - Common utility methods
    """

    __abstract__ = True

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseModel":
        """Create model instance from dictionary."""
        # Filter out non-column attributes
        column_names = {column.name for column in cls.__table__.columns}
        filtered_data = {k: v for k, v in data.items() if k in column_names}

        return cls(**filtered_data)


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate UUID string format.

    Args:
        uuid_string: String to validate as UUID

    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False


def uuid_to_string(uuid_obj: uuid.UUID | str | None) -> str | None:
    """
    Convert UUID object to string, handling None values.

    Args:
        uuid_obj: UUID object or string

    Returns:
        String representation or None
    """
    if uuid_obj is None:
        return None
    if isinstance(uuid_obj, str):
        return uuid_obj
    return str(uuid_obj)


def string_to_uuid(uuid_string: str | None) -> uuid.UUID | None:
    """
    Convert string to UUID object, handling None values.

    Args:
        uuid_string: UUID string

    Returns:
        UUID object or None
    """
    if uuid_string is None:
        return None
    if isinstance(uuid_string, uuid.UUID):
        return uuid_string
    try:
        return uuid.UUID(uuid_string)
    except (ValueError, TypeError):
        return None
