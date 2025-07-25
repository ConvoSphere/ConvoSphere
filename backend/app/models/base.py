"""
Base model for all database entities.

This module provides the base SQLAlchemy model with common fields and functionality
used across all database entities in the AI Assistant Platform.
"""

from typing import Any

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base, declared_attr


class Base:
    """Base class for all database models."""

    @declared_attr
    def __tablename__(self) -> str:
        """Generate table name from class name."""
        return self.__name__.lower()

    # Common fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'N/A')})>"


# Create declarative base using SQLAlchemy 2.0 syntax
Base = declarative_base(cls=Base)
