"""
RBAC (Role-Based Access Control) schemas.

This module defines Pydantic models for RBAC-related operations including
permissions, ABAC rules, and policies.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.app.models.permissions import PermissionAction, PermissionResource


class PermissionBase(BaseModel):
    """Base permission schema."""

    name: str = Field(..., description="Permission name")
    description: str | None = Field(None, description="Permission description")
    resource: PermissionResource = Field(..., description="Resource type")
    action: PermissionAction = Field(..., description="Action type")
    is_active: bool = Field(True, description="Whether permission is active")


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""


class PermissionUpdate(BaseModel):
    """Schema for updating a permission."""

    name: str | None = Field(None, description="Permission name")
    description: str | None = Field(None, description="Permission description")
    resource: PermissionResource | None = Field(None, description="Resource type")
    action: PermissionAction | None = Field(None, description="Action type")
    is_active: bool | None = Field(None, description="Whether permission is active")


class PermissionResponse(PermissionBase):
    """Schema for permission response."""

    id: int = Field(..., description="Permission ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ABACRuleBase(BaseModel):
    """Base ABAC rule schema."""

    name: str = Field(..., description="Rule name")
    description: str | None = Field(None, description="Rule description")
    resource_type: str = Field(..., description="Resource type")
    action: str = Field(..., description="Action type")
    effect: str = Field(..., description="Rule effect (allow/deny)")
    conditions: dict[str, Any] = Field(..., description="Rule conditions")
    is_active: bool = Field(True, description="Whether rule is active")


class ABACRuleCreate(ABACRuleBase):
    """Schema for creating a new ABAC rule."""


class ABACRuleUpdate(BaseModel):
    """Schema for updating an ABAC rule."""

    name: str | None = Field(None, description="Rule name")
    description: str | None = Field(None, description="Rule description")
    resource_type: str | None = Field(None, description="Resource type")
    action: str | None = Field(None, description="Action type")
    effect: str | None = Field(None, description="Rule effect")
    conditions: dict[str, Any] | None = Field(None, description="Rule conditions")
    is_active: bool | None = Field(None, description="Whether rule is active")


class ABACRuleResponse(ABACRuleBase):
    """Schema for ABAC rule response."""

    id: int = Field(..., description="Rule ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ABACPolicyBase(BaseModel):
    """Base ABAC policy schema."""

    name: str = Field(..., description="Policy name")
    description: str | None = Field(None, description="Policy description")
    rules: list[int] = Field(..., description="List of rule IDs")
    is_active: bool = Field(True, description="Whether policy is active")


class ABACPolicyCreate(ABACPolicyBase):
    """Schema for creating a new ABAC policy."""


class ABACPolicyUpdate(BaseModel):
    """Schema for updating an ABAC policy."""

    name: str | None = Field(None, description="Policy name")
    description: str | None = Field(None, description="Policy description")
    rules: list[int] | None = Field(None, description="List of rule IDs")
    is_active: bool | None = Field(None, description="Whether policy is active")


class ABACPolicyResponse(ABACPolicyBase):
    """Schema for ABAC policy response."""

    id: int = Field(..., description="Policy ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class PermissionTest(BaseModel):
    """Schema for testing permissions."""

    user_id: int = Field(..., description="User ID")
    resource: str = Field(..., description="Resource to test")
    action: str = Field(..., description="Action to test")
    context: dict[str, Any] | None = Field(None, description="Additional context")


class PermissionTestResponse(BaseModel):
    """Schema for permission test response."""

    allowed: bool = Field(..., description="Whether access is allowed")
    reason: str = Field(..., description="Reason for decision")
    applied_rules: list[str] = Field(..., description="List of applied rules")


class RBACStats(BaseModel):
    """Schema for RBAC statistics."""

    total_permissions: int = Field(..., description="Total number of permissions")
    total_rules: int = Field(..., description="Total number of ABAC rules")
    total_policies: int = Field(..., description="Total number of ABAC policies")
    active_permissions: int = Field(..., description="Number of active permissions")
    active_rules: int = Field(..., description="Number of active ABAC rules")
    active_policies: int = Field(..., description="Number of active ABAC policies")


class CacheStats(BaseModel):
    """Schema for cache statistics."""

    cache_hits: int = Field(..., description="Number of cache hits")
    cache_misses: int = Field(..., description="Number of cache misses")
    cache_size: int = Field(..., description="Current cache size")
    cache_evictions: int = Field(..., description="Number of cache evictions")


class PerformanceStats(BaseModel):
    """Schema for performance statistics."""

    avg_response_time: float = Field(..., description="Average response time in ms")
    total_requests: int = Field(..., description="Total number of requests")
    error_rate: float = Field(..., description="Error rate percentage")
    throughput: float = Field(..., description="Requests per second")


class SecurityEvent(BaseModel):
    """Schema for security events."""

    id: int = Field(..., description="Event ID")
    event_type: str = Field(..., description="Type of security event")
    user_id: int | None = Field(None, description="User ID involved")
    description: str = Field(..., description="Event description")
    severity: str = Field(..., description="Event severity")
    timestamp: datetime = Field(..., description="Event timestamp")
    details: dict[str, Any] | None = Field(None, description="Additional details")

    class Config:
        from_attributes = True


class PermissionMatrix(BaseModel):
    """Schema for permission matrix."""

    resources: list[str] = Field(..., description="List of resources")
    actions: list[str] = Field(..., description="List of actions")
    matrix: dict[str, dict[str, bool]] = Field(..., description="Permission matrix")
