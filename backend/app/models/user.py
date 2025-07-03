"""
User model for authentication and authorization.

This module defines the User model with role-based access control (RBAC)
and authentication functionality with enterprise features support.
"""

from enum import Enum
from typing import List
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from .base import Base


class UserRole(str, Enum):
    """User roles for RBAC."""
    SUPER_ADMIN = "super_admin"  # Enterprise super admin
    ADMIN = "admin"              # Organization admin
    MANAGER = "manager"          # Team manager
    USER = "user"                # Regular user
    GUEST = "guest"              # Limited access user


class UserStatus(str, Enum):
    """User status for account management."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    ARCHIVED = "archived"


class AuthProvider(str, Enum):
    """Authentication providers."""
    LOCAL = "local"
    LDAP = "ldap"
    SAML = "saml"
    OAUTH_GOOGLE = "oauth_google"
    OAUTH_MICROSOFT = "oauth_microsoft"
    OAUTH_GITHUB = "oauth_github"
    OAUTH_GITLAB = "oauth_gitlab"


# Association table for user groups
user_group_association = Table(
    'user_group_association',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('group_id', UUID(as_uuid=True), ForeignKey('user_groups.id'), primary_key=True)
)


class UserGroup(Base):
    """User group model for enterprise organization."""
    
    __tablename__ = "user_groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # For multi-tenant support
    
    # Group settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System groups cannot be deleted
    
    # Permissions and settings
    permissions = Column(JSONB, nullable=True)  # Custom permissions for the group
    settings = Column(JSONB, nullable=True)     # Group-specific settings
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_group_association, back_populates="groups")
    
    def __repr__(self) -> str:
        """String representation of the group."""
        return f"<UserGroup(id={self.id}, name='{self.name}')>"


class User(Base):
    """User model for authentication and authorization with enterprise features."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for SSO users
    
    # Enterprise fields
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Multi-tenant support
    department = Column(String(200), nullable=True)
    job_title = Column(String(200), nullable=True)
    employee_id = Column(String(100), nullable=True, index=True)
    
    # SSO and external authentication
    auth_provider = Column(SQLEnum(AuthProvider), default=AuthProvider.LOCAL, nullable=False)
    external_id = Column(String(255), nullable=True, index=True)  # ID from external provider
    sso_attributes = Column(JSONB, nullable=True)  # Additional SSO attributes
    
    # Profile fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    display_name = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Status and permissions
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # Security and verification
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(String(10), default="0", nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Preferences
    language = Column(String(10), default="de", nullable=False)
    timezone = Column(String(50), default="Europe/Berlin", nullable=False)
    preferences = Column(JSONB, nullable=True)  # User preferences
    
    # Timestamps
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    groups = relationship("UserGroup", secondary=user_group_association, back_populates="users")
    assistants = relationship("Assistant", back_populates="creator")
    conversations = relationship("Conversation", back_populates="user")
    created_tools = relationship("Tool", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="user")
    documents = relationship("Document", back_populates="user")
    search_queries = relationship("SearchQuery", back_populates="user")
    
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
    
    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.locked_until:
            from datetime import datetime
            return datetime.utcnow() < self.locked_until
        return False
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission based on role and groups."""
        # Check role-based permissions
        role_permissions = {
            UserRole.SUPER_ADMIN: ["*"],  # All permissions
            UserRole.ADMIN: [
                "assistant:read", "assistant:write", "assistant:delete",
                "conversation:read", "conversation:write", "conversation:delete",
                "user:read", "user:write", "user:delete",
                "tool:read", "tool:write", "tool:delete",
                "knowledge:read", "knowledge:write", "knowledge:delete",
                "group:read", "group:write", "group:delete",
                "organization:read", "organization:write"
            ],
            UserRole.MANAGER: [
                "assistant:read", "assistant:write", "assistant:delete",
                "conversation:read", "conversation:write", "conversation:delete",
                "user:read", "user:write",
                "tool:read", "tool:write",
                "knowledge:read", "knowledge:write", "knowledge:delete",
                "group:read"
            ],
            UserRole.USER: [
                "assistant:read", "assistant:write",
                "conversation:read", "conversation:write",
                "tool:read",
                "knowledge:read", "knowledge:write",
                "user:read_own", "user:write_own"
            ],
            UserRole.GUEST: [
                "assistant:read",
                "conversation:read",
                "user:read_own"
            ]
        }
        
        user_permissions = role_permissions.get(self.role, [])
        if "*" in user_permissions:
            return True
        
        if permission in user_permissions:
            return True
        
        # Check group-based permissions
        for group in self.groups:
            if group.permissions and permission in group.permissions:
                return True
        
        return False
    
    def can_access_assistant(self, assistant_id: str) -> bool:
        """Check if user can access specific assistant."""
        if self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER]:
            return True
        # TODO: Implement assistant-specific permissions
        return True
    
    def can_manage_user(self, target_user_id: str) -> bool:
        """Check if user can manage another user."""
        if self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            return True
        if self.role == UserRole.MANAGER:
            # Managers can manage users in their groups
            target_user = None  # TODO: Get target user from database
            if target_user:
                return any(group in self.groups for group in target_user.groups)
        return False
    
    def get_effective_permissions(self) -> List[str]:
        """Get all effective permissions for the user."""
        permissions = set()
        
        # Role-based permissions
        role_permissions = {
            UserRole.SUPER_ADMIN: ["*"],
            UserRole.ADMIN: [
                "assistant:read", "assistant:write", "assistant:delete",
                "conversation:read", "conversation:write", "conversation:delete",
                "user:read", "user:write", "user:delete",
                "tool:read", "tool:write", "tool:delete",
                "knowledge:read", "knowledge:write", "knowledge:delete",
                "group:read", "group:write", "group:delete",
                "organization:read", "organization:write"
            ],
            UserRole.MANAGER: [
                "assistant:read", "assistant:write", "assistant:delete",
                "conversation:read", "conversation:write", "conversation:delete",
                "user:read", "user:write",
                "tool:read", "tool:write",
                "knowledge:read", "knowledge:write", "knowledge:delete",
                "group:read"
            ],
            UserRole.USER: [
                "assistant:read", "assistant:write",
                "conversation:read", "conversation:write",
                "tool:read",
                "knowledge:read", "knowledge:write",
                "user:read_own", "user:write_own"
            ],
            UserRole.GUEST: [
                "assistant:read",
                "conversation:read",
                "user:read_own"
            ]
        }
        
        permissions.update(role_permissions.get(self.role, []))
        
        # Group-based permissions
        for group in self.groups:
            if group.permissions:
                permissions.update(group.permissions)
        
        return list(permissions) 