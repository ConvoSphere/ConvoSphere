"""
Pydantic schemas for user management with enterprise features.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from uuid import UUID

from ..models.user import UserRole, UserStatus, AuthProvider


class UserGroupBase(BaseModel):
    """Base schema for user groups."""
    name: str = Field(..., min_length=1, max_length=200, description="Group name")
    description: Optional[str] = Field(None, max_length=1000, description="Group description")
    organization_id: Optional[UUID] = Field(None, description="Organization ID for multi-tenant support")
    permissions: Optional[List[str]] = Field(None, description="Custom permissions for the group")
    settings: Optional[Dict[str, Any]] = Field(None, description="Group-specific settings")


class UserGroupCreate(UserGroupBase):
    """Schema for creating a user group."""
    pass


class UserGroupUpdate(BaseModel):
    """Schema for updating a user group."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    permissions: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None


class UserGroupResponse(UserGroupBase):
    """Schema for user group responses."""
    id: UUID
    is_active: bool
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime]
    user_count: Optional[int] = Field(None, description="Number of users in the group")

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Base schema for users."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    display_name: Optional[str] = Field(None, max_length=200, description="Display name")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    bio: Optional[str] = Field(None, max_length=2000, description="User bio")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    
    # Enterprise fields
    organization_id: Optional[UUID] = Field(None, description="Organization ID")
    department: Optional[str] = Field(None, max_length=200, description="Department")
    job_title: Optional[str] = Field(None, max_length=200, description="Job title")
    employee_id: Optional[str] = Field(None, max_length=100, description="Employee ID")
    
    # Authentication
    auth_provider: AuthProvider = Field(AuthProvider.LOCAL, description="Authentication provider")
    external_id: Optional[str] = Field(None, max_length=255, description="External provider ID")
    
    # Status and role
    status: UserStatus = Field(UserStatus.ACTIVE, description="User status")
    role: UserRole = Field(UserRole.USER, description="User role")
    
    # Preferences
    language: str = Field("de", max_length=10, description="Preferred language")
    timezone: str = Field("Europe/Berlin", max_length=50, description="Timezone")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: Optional[str] = Field(None, min_length=8, description="Password (required for local auth)")
    sso_attributes: Optional[Dict[str, Any]] = Field(None, description="SSO attributes")
    group_ids: Optional[List[UUID]] = Field(None, description="Group IDs to assign")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v, info):
        """Validate password is provided for local authentication."""
        auth_provider = info.data.get('auth_provider', AuthProvider.LOCAL)
        if auth_provider == AuthProvider.LOCAL and not v:
            raise ValueError('Password is required for local authentication')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=2000)
    phone: Optional[str] = Field(None, max_length=50)
    
    # Enterprise fields
    organization_id: Optional[UUID] = None
    department: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=200)
    employee_id: Optional[str] = Field(None, max_length=100)
    
    # Status and role
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    
    # Preferences
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    preferences: Optional[Dict[str, Any]] = None


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password."""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(UserBase):
    """Schema for user responses."""
    id: UUID
    is_verified: bool
    email_verified_at: Optional[datetime]
    password_changed_at: Optional[datetime]
    failed_login_attempts: str
    locked_until: Optional[datetime]
    last_login: Optional[datetime]
    last_activity: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    groups: List[UserGroupResponse] = []
    effective_permissions: List[str] = []
    
    # Computed properties
    full_name: str
    is_active: bool
    is_locked: bool

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for user list responses."""
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int


class UserBulkUpdate(BaseModel):
    """Schema for bulk user updates."""
    user_ids: List[UUID] = Field(..., description="User IDs to update")
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    organization_id: Optional[UUID] = None
    group_ids: Optional[List[UUID]] = None


class UserGroupAssignment(BaseModel):
    """Schema for assigning users to groups."""
    user_ids: List[UUID] = Field(..., description="User IDs to assign")
    group_ids: List[UUID] = Field(..., description="Group IDs to assign users to")
    operation: str = Field("add", pattern="^(add|remove)$", description="Operation: add or remove")


class UserSearchParams(BaseModel):
    """Schema for user search parameters."""
    query: Optional[str] = Field(None, description="Search query")
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    auth_provider: Optional[AuthProvider] = None
    organization_id: Optional[UUID] = None
    group_id: Optional[UUID] = None
    is_verified: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_login_after: Optional[datetime] = None
    last_login_before: Optional[datetime] = None
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
    users_by_role: Dict[str, int]
    users_by_auth_provider: Dict[str, int]
    users_by_status: Dict[str, int]
    recent_registrations: int  # Last 30 days
    recent_logins: int  # Last 7 days


class SSOUserCreate(BaseModel):
    """Schema for creating users via SSO."""
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    auth_provider: AuthProvider
    external_id: str
    sso_attributes: Dict[str, Any]
    organization_id: Optional[UUID] = None
    role: UserRole = UserRole.USER
    group_ids: Optional[List[UUID]] = None


class UserProfileUpdate(BaseModel):
    """Schema for users updating their own profile."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=2000)
    phone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    preferences: Optional[Dict[str, Any]] = None 