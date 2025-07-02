"""
User model for authentication and authorization.

This module defines the User model with role-based access control (RBAC)
and authentication functionality.
"""

from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base


class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    display_name = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Status and permissions
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # Preferences
    language = Column(String(10), default="de", nullable=False)
    timezone = Column(String(50), default="Europe/Berlin", nullable=False)
    
    # Timestamps
    last_login = Column(String(50), nullable=True)  # ISO format string
    email_verified_at = Column(String(50), nullable=True)  # ISO format string
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.display_name:
            return self.display_name
        return self.username
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission based on role."""
        role_permissions = {
            UserRole.ADMIN: ["*"],  # All permissions
            UserRole.MANAGER: [
                "assistant:read", "assistant:write", "assistant:delete",
                "conversation:read", "conversation:write", "conversation:delete",
                "user:read", "user:write",
                "tool:read", "tool:write"
            ],
            UserRole.USER: [
                "assistant:read", "assistant:write",
                "conversation:read", "conversation:write",
                "tool:read"
            ],
            UserRole.GUEST: [
                "assistant:read",
                "conversation:read"
            ]
        }
        
        user_permissions = role_permissions.get(self.role, [])
        return "*" in user_permissions or permission in user_permissions
    
    def can_access_assistant(self, assistant_id: str) -> bool:
        """Check if user can access specific assistant."""
        if self.role in [UserRole.ADMIN, UserRole.MANAGER]:
            return True
        # TODO: Implement assistant-specific permissions
        return True 