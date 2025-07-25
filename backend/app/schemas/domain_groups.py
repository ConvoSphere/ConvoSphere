"""
Pydantic schemas for domain group management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..models.domain_groups import AccessLevel, DomainType, ResourceType


class DomainGroupBase(BaseModel):
    """Base schema for domain groups."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Domain group name")
    description: str | None = Field(None, max_length=2000, description="Domain group description")
    display_name: str | None = Field(None, max_length=200, description="Display name")
    
    # Domain categorization
    domain_type: DomainType = Field(..., description="Type of domain group")
    parent_domain_id: UUID | None = Field(None, description="Parent domain group ID")
    
    # Organization and metadata
    organization_id: UUID | None = Field(None, description="Organization ID")
    external_id: str | None = Field(None, max_length=255, description="External system ID")
    tags: List[str] | None = Field(None, description="Tags for categorization")
    
    # Domain settings
    is_public: bool = Field(False, description="Whether domain group is public")
    default_access_level: AccessLevel = Field(AccessLevel.READ_WRITE, description="Default access level for new members")
    allow_self_join: bool = Field(False, description="Allow users to join without invitation")
    require_approval: bool = Field(True, description="Require approval for new members")
    
    # Domain-specific settings
    settings: Dict[str, Any] | None = Field(None, description="Domain-specific configuration")
    permissions: List[str] | None = Field(None, description="Custom permissions for the domain")


class DomainGroupCreate(DomainGroupBase):
    """Schema for creating a domain group."""
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        """Validate tags."""
        if v is not None:
            if len(v) > 20:
                raise ValueError("Maximum 20 tags allowed")
            for tag in v:
                if len(tag) > 50:
                    raise ValueError("Tag length must be <= 50 characters")
        return v


class DomainGroupUpdate(BaseModel):
    """Schema for updating a domain group."""
    
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    display_name: str | None = Field(None, max_length=200)
    domain_type: DomainType | None = None
    parent_domain_id: UUID | None = None
    external_id: str | None = Field(None, max_length=255)
    tags: List[str] | None = None
    is_public: bool | None = None
    default_access_level: AccessLevel | None = None
    allow_self_join: bool | None = None
    require_approval: bool | None = None
    settings: Dict[str, Any] | None = None
    permissions: List[str] | None = None


class DomainGroupResponse(DomainGroupBase):
    """Schema for domain group responses."""
    
    id: UUID
    is_active: bool
    is_system: bool
    member_count: int
    resource_count: int
    created_at: datetime
    updated_at: datetime | None
    expires_at: datetime | None
    
    # Computed properties
    is_expired: bool
    
    model_config = ConfigDict(from_attributes=True)


class DomainMemberBase(BaseModel):
    """Base schema for domain members."""
    
    user_id: UUID = Field(..., description="User ID")
    access_level: AccessLevel = Field(AccessLevel.READ_WRITE, description="Access level in domain")
    is_active: bool = Field(True, description="Whether membership is active")


class DomainMemberCreate(DomainMemberBase):
    """Schema for adding domain members."""
    
    invited_by: UUID | None = Field(None, description="User who sent the invitation")


class DomainMemberUpdate(BaseModel):
    """Schema for updating domain members."""
    
    access_level: AccessLevel | None = None
    is_active: bool | None = None


class DomainMemberResponse(DomainMemberBase):
    """Schema for domain member responses."""
    
    joined_at: datetime
    invited_by: UUID | None
    
    # User information
    user_email: str
    user_name: str
    user_role: str
    
    model_config = ConfigDict(from_attributes=True)


class DomainResourceBase(BaseModel):
    """Base schema for domain resources."""
    
    resource_id: str = Field(..., max_length=255, description="Resource identifier")
    resource_type: ResourceType = Field(..., description="Type of resource")
    resource_name: str | None = Field(None, max_length=200, description="Resource name")
    
    # Access control
    access_level: AccessLevel = Field(AccessLevel.READ_WRITE, description="Access level for this resource")
    is_public: bool = Field(False, description="Whether resource is public within domain")
    
    # Metadata
    description: str | None = Field(None, max_length=2000, description="Resource description")
    tags: List[str] | None = Field(None, description="Resource tags")
    metadata: Dict[str, Any] | None = Field(None, description="Additional metadata")


class DomainResourceCreate(DomainResourceBase):
    """Schema for adding domain resources."""
    
    added_by: UUID | None = Field(None, description="User who added the resource")


class DomainResourceUpdate(BaseModel):
    """Schema for updating domain resources."""
    
    resource_name: str | None = Field(None, max_length=200)
    access_level: AccessLevel | None = None
    is_public: bool | None = None
    description: str | None = Field(None, max_length=2000)
    tags: List[str] | None = None
    metadata: Dict[str, Any] | None = None


class DomainResourceResponse(DomainResourceBase):
    """Schema for domain resource responses."""
    
    id: UUID
    domain_group_id: UUID
    is_active: bool
    added_at: datetime
    updated_at: datetime | None
    expires_at: datetime | None
    added_by: UUID | None
    
    # Computed properties
    is_expired: bool
    
    model_config = ConfigDict(from_attributes=True)


class DomainInvitationBase(BaseModel):
    """Base schema for domain invitations."""
    
    email: str = Field(..., description="Email address to invite")
    access_level: AccessLevel = Field(AccessLevel.READ_WRITE, description="Access level for invited user")
    message: str | None = Field(None, max_length=1000, description="Invitation message")


class DomainInvitationCreate(DomainInvitationBase):
    """Schema for creating domain invitations."""
    
    expires_in_days: int = Field(7, ge=1, le=30, description="Days until invitation expires")


class DomainInvitationResponse(DomainInvitationBase):
    """Schema for domain invitation responses."""
    
    id: UUID
    domain_group_id: UUID
    user_id: UUID | None
    status: str
    token: str
    expires_at: datetime
    created_at: datetime
    accepted_at: datetime | None
    
    # Computed properties
    is_expired: bool
    
    model_config = ConfigDict(from_attributes=True)


class DomainActivityResponse(BaseModel):
    """Schema for domain activity responses."""
    
    id: UUID
    domain_group_id: UUID
    user_id: UUID | None
    activity_type: str
    resource_type: ResourceType | None
    resource_id: str | None
    description: str
    details: Dict[str, Any] | None
    created_at: datetime
    
    # User information
    user_email: str | None
    user_name: str | None
    
    model_config = ConfigDict(from_attributes=True)


class DomainGroupStats(BaseModel):
    """Schema for domain group statistics."""
    
    total_domains: int
    active_domains: int
    total_members: int
    total_resources: int
    domains_by_type: Dict[str, int]
    recent_activities: int  # Last 7 days
    pending_invitations: int


class DomainSearchParams(BaseModel):
    """Schema for domain search parameters."""
    
    query: str | None = Field(None, description="Search query")
    domain_type: DomainType | None = None
    organization_id: UUID | None = None
    parent_domain_id: UUID | None = None
    is_public: bool | None = None
    is_active: bool | None = None
    tags: List[str] | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")


class DomainGroupListResponse(BaseModel):
    """Schema for domain group list responses."""
    
    domains: List[DomainGroupResponse]
    total: int
    page: int
    size: int
    pages: int


class DomainHierarchyResponse(BaseModel):
    """Schema for domain hierarchy responses."""
    
    domain_id: UUID
    name: str
    domain_type: DomainType
    level: int
    children: List["DomainHierarchyResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


# Update forward reference
DomainHierarchyResponse.model_rebuild()