"""
Pydantic schemas for user management with enterprise features.
"""

import re
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..models.user import AuthProvider, UserRole, UserStatus


def validate_email(email: str) -> str:
    """Custom email validator that allows local domains for development."""
    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email


class UserGroupBase(BaseModel):
    """Base schema for user groups."""

    name: str = Field(..., min_length=1, max_length=200, description="Group name")
    description: str | None = Field(
        None,
        max_length=1000,
        description="Group description",
    )
    organization_id: UUID | None = Field(
        None,
        description="Organization ID for multi-tenant support",
    )
    permissions: list[str] | None = Field(
        None,
        description="Custom permissions for the group",
    )
    settings: dict[str, Any] | None = Field(None, description="Group-specific settings")


class UserGroupCreate(UserGroupBase):
    """Schema for creating a user group."""


class UserGroupUpdate(BaseModel):
    """Schema for updating a user group."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    permissions: list[str] | None = None
    settings: dict[str, Any] | None = None


class UserGroupResponse(UserGroupBase):
    """Schema for user group responses."""

    id: UUID
    is_active: bool
    is_system: bool
    created_at: datetime
    updated_at: datetime | None
    user_count: int | None = Field(None, description="Number of users in the group")

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Base schema for users."""

    email: str = Field(..., description="User email address")

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v):
        return validate_email(v)
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    first_name: str | None = Field(None, max_length=100, description="First name")
    last_name: str | None = Field(None, max_length=100, description="Last name")
    display_name: str | None = Field(None, max_length=200, description="Display name")
    avatar_url: str | None = Field(None, max_length=500, description="Avatar URL")
    bio: str | None = Field(None, max_length=2000, description="User bio")
    phone: str | None = Field(None, max_length=50, description="Phone number")

    # Enterprise fields
    organization_id: UUID | None = Field(None, description="Organization ID")
    department: str | None = Field(None, max_length=200, description="Department")
    job_title: str | None = Field(None, max_length=200, description="Job title")
    employee_id: str | None = Field(None, max_length=100, description="Employee ID")

    # Authentication
    auth_provider: AuthProvider = Field(
        AuthProvider.LOCAL,
        description="Authentication provider",
    )
    external_id: str | None = Field(
        None,
        max_length=255,
        description="External provider ID",
    )

    # Status and role
    status: UserStatus = Field(UserStatus.ACTIVE, description="User status")
    role: UserRole = Field(UserRole.USER, description="User role")

    # Preferences
    language: str = Field("de", max_length=10, description="Preferred language")
    timezone: str = Field("Europe/Berlin", max_length=50, description="Timezone")
    preferences: dict[str, Any] | None = Field(None, description="User preferences")


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str | None = Field(
        None,
        min_length=8,
        description="Password (required for local auth)",
    )
    sso_attributes: dict[str, Any] | None = Field(None, description="SSO attributes")
    group_ids: list[UUID] | None = Field(None, description="Group IDs to assign")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v, info):
        """Validate password is provided for local authentication."""
        auth_provider = info.data.get("auth_provider", AuthProvider.LOCAL)
        if auth_provider == AuthProvider.LOCAL and not v:
            raise ValueError("Password is required for local authentication")
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v):
        if v is None:
            return v
        return validate_email(v)
    username: str | None = Field(None, min_length=3, max_length=100)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    display_name: str | None = Field(None, max_length=200)
    avatar_url: str | None = Field(None, max_length=500)
    bio: str | None = Field(None, max_length=2000)
    phone: str | None = Field(None, max_length=50)

    # Enterprise fields
    organization_id: UUID | None = None
    department: str | None = Field(None, max_length=200)
    job_title: str | None = Field(None, max_length=200)
    employee_id: str | None = Field(None, max_length=100)

    # Status and role
    status: UserStatus | None = None
    role: UserRole | None = None

    # Preferences
    language: str | None = Field(None, max_length=10)
    timezone: str | None = Field(None, max_length=50)
    preferences: dict[str, Any] | None = None


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password."""

    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(UserBase):
    """Schema for user responses."""

    id: UUID
    is_verified: bool
    email_verified_at: datetime | None
    password_changed_at: datetime | None
    failed_login_attempts: str
    locked_until: datetime | None
    last_login: datetime | None
    last_activity: datetime | None
    created_at: datetime
    updated_at: datetime | None
    groups: list[UserGroupResponse] = []
    effective_permissions: list[str] = []

    # Computed properties
    full_name: str
    is_active: bool
    is_locked: bool

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for user list responses."""

    users: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int


class UserBulkUpdate(BaseModel):
    """Schema for bulk user updates."""

    user_ids: list[UUID] = Field(..., description="User IDs to update")
    status: UserStatus | None = None
    role: UserRole | None = None
    organization_id: UUID | None = None
    group_ids: list[UUID] | None = None


class UserGroupAssignment(BaseModel):
    """Schema for assigning users to groups."""

    user_ids: list[UUID] = Field(..., description="User IDs to assign")
    group_ids: list[UUID] = Field(..., description="Group IDs to assign users to")
    operation: str = Field(
        "add",
        pattern="^(add|remove)$",
        description="Operation: add or remove",
    )


class UserSearchParams(BaseModel):
    """Schema for user search parameters."""

    query: str | None = Field(None, description="Search query")
    role: UserRole | None = None
    status: UserStatus | None = None
    auth_provider: AuthProvider | None = None
    organization_id: UUID | None = None
    group_id: UUID | None = None
    is_verified: bool | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    last_login_after: datetime | None = None
    last_login_before: datetime | None = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")


class UserStats(BaseModel):
    """Schema for user statistics."""

    total_users: int
    active_users: int
    inactive_users: int
    suspended_users: int
    pending_users: int
    verified_users: int
    users_by_role: dict[str, int]
    users_by_auth_provider: dict[str, int]
    users_by_status: dict[str, int]
    recent_registrations: int  # Last 30 days
    recent_logins: int  # Last 7 days


class SSOUserCreate(BaseModel):
    """Schema for creating users via SSO."""

    email: str

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v):
        return validate_email(v)
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    auth_provider: AuthProvider
    external_id: str
    sso_attributes: dict[str, Any]
    organization_id: UUID | None = None
    role: UserRole = UserRole.USER
    group_ids: list[UUID] | None = None


class UserProfileUpdate(BaseModel):
    """Schema for users updating their own profile."""

    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    display_name: str | None = Field(None, max_length=200)
    avatar_url: str | None = Field(None, max_length=500)
    bio: str | None = Field(None, max_length=2000)
    phone: str | None = Field(None, max_length=50)
    language: str | None = Field(None, max_length=10)
    timezone: str | None = Field(None, max_length=50)
    preferences: dict[str, Any] | None = None
