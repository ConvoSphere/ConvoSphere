"""
Advanced RBAC management API endpoints.

This module provides API endpoints for managing granular permissions,
ABAC rules, security policies, and monitoring RBAC performance.
"""

from datetime import datetime
from typing import Any

from app.core.database import get_db
from app.core.rbac_cache import rbac_cache, rbac_performance_monitor
from app.core.security import get_current_user
from app.models.permissions import (
    PermissionAction,
    PermissionResource,
)
from app.models.user import User, UserRole
from app.schemas.rbac import (
    ABACPolicyCreate,
    ABACPolicyResponse,
    ABACRuleCreate,
    ABACRuleResponse,
    ABACRuleUpdate,
    CacheStats,
    PerformanceStats,
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
    RBACStats,
)
from app.services.rbac_service import RBACService
from app.utils.exceptions import PermissionDeniedError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


# Permission Management
@router.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new permission."""
    try:
        rbac_service = RBACService(db)
        permission = rbac_service.create_permission(permission_data, current_user)
        return rbac_service._permission_to_response(permission)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    resource: PermissionResource | None = Query(None, description="Filter by resource"),
    action: PermissionAction | None = Query(None, description="Filter by action"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List permissions with filtering."""
    try:
        rbac_service = RBACService(db)
        permissions = rbac_service.list_permissions(
            resource=resource,
            action=action,
            is_active=is_active,
            current_user=current_user,
        )
        return [rbac_service._permission_to_response(p) for p in permissions]
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get permission by ID."""
    try:
        rbac_service = RBACService(db)
        permission = rbac_service.get_permission_by_id(permission_id, current_user)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found",
            )
        return rbac_service._permission_to_response(permission)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: str,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update permission."""
    try:
        rbac_service = RBACService(db)
        permission = rbac_service.update_permission(
            permission_id, permission_data, current_user,
        )
        return rbac_service._permission_to_response(permission)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete permission."""
    try:
        rbac_service = RBACService(db)
        rbac_service.delete_permission(permission_id, current_user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ABAC Rule Management
@router.post(
    "/abac/rules", response_model=ABACRuleResponse, status_code=status.HTTP_201_CREATED,
)
async def create_abac_rule(
    rule_data: ABACRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new ABAC rule."""
    try:
        rbac_service = RBACService(db)
        rule = rbac_service.create_abac_rule(rule_data, current_user)
        return rbac_service._abac_rule_to_response(rule)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/abac/rules", response_model=list[ABACRuleResponse])
async def list_abac_rules(
    resource_type: str | None = Query(None, description="Filter by resource type"),
    action: str | None = Query(None, description="Filter by action"),
    effect: str | None = Query(None, description="Filter by effect"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List ABAC rules with filtering."""
    try:
        rbac_service = RBACService(db)
        rules = rbac_service.list_abac_rules(
            resource_type=resource_type,
            action=action,
            effect=effect,
            is_active=is_active,
            current_user=current_user,
        )
        return [rbac_service._abac_rule_to_response(r) for r in rules]
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/abac/rules/{rule_id}", response_model=ABACRuleResponse)
async def get_abac_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ABAC rule by ID."""
    try:
        rbac_service = RBACService(db)
        rule = rbac_service.get_abac_rule_by_id(rule_id, current_user)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ABAC rule not found",
            )
        return rbac_service._abac_rule_to_response(rule)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/abac/rules/{rule_id}", response_model=ABACRuleResponse)
async def update_abac_rule(
    rule_id: str,
    rule_data: ABACRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update ABAC rule."""
    try:
        rbac_service = RBACService(db)
        rule = rbac_service.update_abac_rule(rule_id, rule_data, current_user)
        return rbac_service._abac_rule_to_response(rule)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/abac/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_abac_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete ABAC rule."""
    try:
        rbac_service = RBACService(db)
        rbac_service.delete_abac_rule(rule_id, current_user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ABAC Policy Management
@router.post(
    "/abac/policies",
    response_model=ABACPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_abac_policy(
    policy_data: ABACPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new ABAC policy."""
    try:
        rbac_service = RBACService(db)
        policy = rbac_service.create_abac_policy(policy_data, current_user)
        return rbac_service._abac_policy_to_response(policy)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/abac/policies", response_model=list[ABACPolicyResponse])
async def list_abac_policies(
    is_active: bool | None = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List ABAC policies."""
    try:
        rbac_service = RBACService(db)
        policies = rbac_service.list_abac_policies(
            is_active=is_active, current_user=current_user,
        )
        return [rbac_service._abac_policy_to_response(p) for p in policies]
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# Permission Testing
@router.post("/test-permission")
async def test_permission(
    user_id: str,
    permission: str,
    resource_id: str | None = None,
    context: dict[str, Any] | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Test permission evaluation for a user."""
    try:
        rbac_service = RBACService(db)
        result = rbac_service.test_permission(
            user_id=user_id,
            permission=permission,
            resource_id=resource_id,
            context=context or {},
            current_user=current_user,
        )
        return {
            "user_id": user_id,
            "permission": permission,
            "resource_id": resource_id,
            "result": result["has_permission"],
            "evaluation_time": result["evaluation_time"],
            "cached": result["cached"],
            "details": result["details"],
        }
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# RBAC Statistics and Monitoring
@router.get("/stats", response_model=RBACStats)
async def get_rbac_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get RBAC statistics."""
    try:
        rbac_service = RBACService(db)
        return rbac_service.get_rbac_stats(current_user)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/cache/stats", response_model=CacheStats)
async def get_cache_stats(
    current_user: User = Depends(get_current_user),
):
    """Get RBAC cache statistics."""
    if not current_user.has_permission("rbac:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions",
        )

    stats = rbac_cache.get_cache_stats()
    return CacheStats(
        user_permissions_count=stats.get("user_permissions:*", 0),
        role_permissions_count=stats.get("role_permissions:*", 0),
        user_groups_count=stats.get("user_groups:*", 0),
        permission_evaluations_count=stats.get("permission_eval:*", 0),
        total_cache_entries=sum(stats.values()),
    )


@router.get("/performance/stats/{user_id}")
async def get_performance_stats(
    user_id: str,
    permission: str | None = Query(None, description="Filter by permission"),
    current_user: User = Depends(get_current_user),
):
    """Get RBAC performance statistics for a user."""
    if not current_user.has_permission("rbac:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions",
        )

    if permission:
        stats = rbac_performance_monitor.get_permission_stats(user_id, permission)
        return PerformanceStats(
            user_id=user_id,
            permission=permission,
            avg_duration=stats["avg_duration"],
            max_duration=stats["max_duration"],
            min_duration=stats["min_duration"],
            total_checks=stats["total_checks"],
            cache_hits=stats["cache_hits"],
            cache_misses=stats["cache_misses"],
            cache_hit_rate=stats["cache_hit_rate"],
        )
    # Return overall stats for user
    return {
        "user_id": user_id,
        "message": "Overall performance stats not yet implemented",
    }


# Cache Management
@router.post("/cache/clear")
async def clear_rbac_cache(
    user_id: str | None = Query(None, description="Clear cache for specific user"),
    current_user: User = Depends(get_current_user),
):
    """Clear RBAC cache."""
    if not current_user.has_permission("rbac:manage"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions",
        )

    if user_id:
        success = rbac_cache.bulk_invalidate_user_cache(user_id)
    else:
        success = rbac_cache.clear_all_cache()

    return {
        "success": success,
        "message": f"Cache cleared for {'user' if user_id else 'all users'}",
    }


# Security Monitoring
@router.get("/security/events")
async def get_security_events(
    event_type: str | None = Query(None, description="Filter by event type"),
    threat_level: str | None = Query(None, description="Filter by threat level"),
    user_id: str | None = Query(None, description="Filter by user ID"),
    limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
    current_user: User = Depends(get_current_user),
):
    """Get security events."""
    if not current_user.has_permission("security:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions",
        )

    # This would integrate with the security monitoring system
    # For now, return a placeholder
    return {
        "events": [],
        "total": 0,
        "message": "Security events monitoring not yet implemented",
    }


# Permission Matrix
@router.get("/permission-matrix")
async def get_permission_matrix(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get permission matrix showing all roles and their permissions."""
    if not current_user.has_permission("rbac:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions",
        )

    # Build permission matrix
    matrix = {}
    for role in UserRole:
        permissions = set()

        # Get role-based permissions
        role_permissions = {
            UserRole.SUPER_ADMIN: ["*"],
            UserRole.ADMIN: [
                "assistant:read",
                "assistant:write",
                "assistant:delete",
                "conversation:read",
                "conversation:write",
                "conversation:delete",
                "user:read",
                "user:write",
                "user:delete",
                "tool:read",
                "tool:write",
                "tool:delete",
                "knowledge:read",
                "knowledge:write",
                "knowledge:delete",
                "group:read",
                "group:write",
                "group:delete",
                "organization:read",
                "organization:write",
            ],
            UserRole.MANAGER: [
                "assistant:read",
                "assistant:write",
                "assistant:delete",
                "conversation:read",
                "conversation:write",
                "conversation:delete",
                "user:read",
                "user:write",
                "tool:read",
                "tool:write",
                "knowledge:read",
                "knowledge:write",
                "knowledge:delete",
                "group:read",
            ],
            UserRole.USER: [
                "assistant:read",
                "assistant:write",
                "conversation:read",
                "conversation:write",
                "tool:read",
                "knowledge:read",
                "knowledge:write",
                "user:read_own",
                "user:write_own",
            ],
            UserRole.GUEST: [
                "assistant:read",
                "conversation:read",
                "user:read_own",
            ],
        }

        permissions.update(role_permissions.get(role, []))
        matrix[role] = sorted(list(permissions))

    return {"permission_matrix": matrix, "generated_at": datetime.now().isoformat()}
