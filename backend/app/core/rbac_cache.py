"""
RBAC caching layer for performance optimization.

This module provides caching mechanisms for RBAC operations to improve
performance and reduce database load.
"""

import json
import time
from functools import wraps
from typing import Any

from app.core.redis_client import get_redis_client
from app.models.user import User, UserRole
from loguru import logger


class RBACCache:
    """RBAC caching layer for performance optimization."""

    def __init__(self):
        self.redis = get_redis_client()
        self.cache_prefix = "rbac:"

        # Cache TTLs (in seconds)
        self.user_permissions_ttl = 300  # 5 minutes
        self.role_permissions_ttl = 1800  # 30 minutes
        self.user_groups_ttl = 600  # 10 minutes
        self.permission_evaluation_ttl = 60  # 1 minute

    def get_user_permissions(self, user_id: str) -> set[str] | None:
        """Get cached user permissions."""
        cache_key = f"{self.cache_prefix}user_permissions:{user_id}"
        cached_data = self.redis.get(cache_key)

        if cached_data:
            permissions = json.loads(cached_data)
            return set(permissions)

        return None

    def set_user_permissions(self, user_id: str, permissions: set[str]) -> bool:
        """Cache user permissions."""
        cache_key = f"{self.cache_prefix}user_permissions:{user_id}"
        return self.redis.setex(
            cache_key,
            self.user_permissions_ttl,
            json.dumps(list(permissions)),
        )

    def invalidate_user_permissions(self, user_id: str) -> bool:
        """Invalidate user permissions cache."""
        cache_key = f"{self.cache_prefix}user_permissions:{user_id}"
        return bool(self.redis.delete(cache_key))

    def get_role_permissions(self, role: UserRole) -> set[str] | None:
        """Get cached role permissions."""
        cache_key = f"{self.cache_prefix}role_permissions:{role}"
        cached_data = self.redis.get(cache_key)

        if cached_data:
            permissions = json.loads(cached_data)
            return set(permissions)

        return None

    def set_role_permissions(self, role: UserRole, permissions: set[str]) -> bool:
        """Cache role permissions."""
        cache_key = f"{self.cache_prefix}role_permissions:{role}"
        return self.redis.setex(
            cache_key,
            self.role_permissions_ttl,
            json.dumps(list(permissions)),
        )

    def get_user_groups(self, user_id: str) -> list[dict[str, Any]] | None:
        """Get cached user groups."""
        cache_key = f"{self.cache_prefix}user_groups:{user_id}"
        cached_data = self.redis.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        return None

    def set_user_groups(self, user_id: str, groups: list[dict[str, Any]]) -> bool:
        """Cache user groups."""
        cache_key = f"{self.cache_prefix}user_groups:{user_id}"
        return self.redis.setex(cache_key, self.user_groups_ttl, json.dumps(groups))

    def invalidate_user_groups(self, user_id: str) -> bool:
        """Invalidate user groups cache."""
        cache_key = f"{self.cache_prefix}user_groups:{user_id}"
        return bool(self.redis.delete(cache_key))

    def get_permission_evaluation(
        self,
        user_id: str,
        permission: str,
        resource_id: str | None = None,
    ) -> bool | None:
        """Get cached permission evaluation result."""
        resource_suffix = f":{resource_id}" if resource_id else ""
        cache_key = f"{self.cache_prefix}permission_eval:{user_id}:{permission}{resource_suffix}"
        cached_result = self.redis.get(cache_key)

        if cached_result is not None:
            return json.loads(cached_result)

        return None

    def set_permission_evaluation(
        self,
        user_id: str,
        permission: str,
        result: bool,
        resource_id: str | None = None,
    ) -> bool:
        """Cache permission evaluation result."""
        resource_suffix = f":{resource_id}" if resource_id else ""
        cache_key = f"{self.cache_prefix}permission_eval:{user_id}:{permission}{resource_suffix}"
        return self.redis.setex(
            cache_key,
            self.permission_evaluation_ttl,
            json.dumps(result),
        )

    def invalidate_permission_evaluation(
        self,
        user_id: str,
        permission: str = None,
    ) -> bool:
        """Invalidate permission evaluation cache."""
        if permission:
            # Invalidate specific permission
            pattern = f"{self.cache_prefix}permission_eval:{user_id}:{permission}*"
        else:
            # Invalidate all permissions for user
            pattern = f"{self.cache_prefix}permission_eval:{user_id}:*"

        keys = self.redis.keys(pattern)
        if keys:
            return bool(self.redis.delete(*keys))
        return True

    def bulk_invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cache entries for a user."""
        patterns = [
            f"{self.cache_prefix}user_permissions:{user_id}",
            f"{self.cache_prefix}user_groups:{user_id}",
            f"{self.cache_prefix}permission_eval:{user_id}:*",
        ]

        deleted = 0
        for pattern in patterns:
            keys = self.redis.keys(pattern)
            if keys:
                deleted += self.redis.delete(*keys)

        return deleted > 0

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        patterns = [
            f"{self.cache_prefix}user_permissions:*",
            f"{self.cache_prefix}role_permissions:*",
            f"{self.cache_prefix}user_groups:*",
            f"{self.cache_prefix}permission_eval:*",
        ]

        stats = {}
        for pattern in patterns:
            keys = self.redis.keys(pattern)
            stats[pattern.replace(self.cache_prefix, "")] = len(keys)

        return stats

    def clear_all_cache(self) -> bool:
        """Clear all RBAC cache."""
        pattern = f"{self.cache_prefix}*"
        keys = self.redis.keys(pattern)

        if keys:
            return bool(self.redis.delete(*keys))
        return True


# Global RBAC cache instance
rbac_cache = RBACCache()


def cache_permission_evaluation(ttl: int = 60):
    """Decorator to cache permission evaluation results."""

    def decorator(func):
        @wraps(func)
        def wrapper(user: User, permission: str, resource: Any = None, *args, **kwargs):
            # Check cache first
            resource_id = (
                str(resource.id) if resource and hasattr(resource, "id") else None
            )
            cached_result = rbac_cache.get_permission_evaluation(
                str(user.id),
                permission,
                resource_id,
            )

            if cached_result is not None:
                logger.debug(f"Cache hit for permission evaluation: {permission}")
                return cached_result

            # Evaluate permission
            result = func(user, permission, resource, *args, **kwargs)

            # Cache result
            rbac_cache.set_permission_evaluation(
                str(user.id),
                permission,
                result,
                resource_id,
            )

            return result

        return wrapper

    return decorator


class CachedUserPermissions:
    """Cached user permissions manager."""

    def __init__(self, user: User):
        self.user = user
        self.user_id = str(user.id)
        self._permissions: set[str] | None = None
        self._groups: list[dict[str, Any]] | None = None

    def get_permissions(self) -> set[str]:
        """Get user permissions with caching."""
        if self._permissions is None:
            # Try cache first
            cached_permissions = rbac_cache.get_user_permissions(self.user_id)

            if cached_permissions is not None:
                self._permissions = cached_permissions
            else:
                # Calculate permissions
                self._permissions = self._calculate_permissions()

                # Cache permissions
                rbac_cache.set_user_permissions(self.user_id, self._permissions)

        return self._permissions

    def get_groups(self) -> list[dict[str, Any]]:
        """Get user groups with caching."""
        if self._groups is None:
            # Try cache first
            cached_groups = rbac_cache.get_user_groups(self.user_id)

            if cached_groups is not None:
                self._groups = cached_groups
            else:
                # Get groups from database
                self._groups = [
                    {
                        "id": str(group.id),
                        "name": group.name,
                        "permissions": group.permissions or [],
                    }
                    for group in self.user.groups
                ]

                # Cache groups
                rbac_cache.set_user_groups(self.user_id, self._groups)

        return self._groups

    def _calculate_permissions(self) -> set[str]:
        """Calculate user permissions."""
        permissions = set()

        # Role-based permissions
        role_permissions = self._get_role_permissions(self.user.role)
        permissions.update(role_permissions)

        # Group-based permissions
        for group in self.user.groups:
            if group.permissions:
                permissions.update(group.permissions)

        return permissions

    def _get_role_permissions(self, role: UserRole) -> set[str]:
        """Get role permissions with caching."""
        # Try cache first
        cached_permissions = rbac_cache.get_role_permissions(role)

        if cached_permissions is not None:
            return cached_permissions

        # Calculate role permissions
        role_permissions = self._calculate_role_permissions(role)

        # Cache role permissions
        rbac_cache.set_role_permissions(role, role_permissions)

        return role_permissions

    def _calculate_role_permissions(self, role: UserRole) -> set[str]:
        """Calculate role permissions."""
        role_permissions = {
            UserRole.SUPER_ADMIN: {"*"},
            UserRole.ADMIN: {
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
            },
            UserRole.MANAGER: {
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
            },
            UserRole.USER: {
                "assistant:read",
                "assistant:write",
                "conversation:read",
                "conversation:write",
                "tool:read",
                "knowledge:read",
                "knowledge:write",
                "user:read_own",
                "user:write_own",
            },
            UserRole.GUEST: {
                "assistant:read",
                "conversation:read",
                "user:read_own",
            },
        }

        return role_permissions.get(role, set())

    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        permissions = self.get_permissions()

        # Check for wildcard permission
        if "*" in permissions:
            return True

        return permission in permissions

    def invalidate_cache(self):
        """Invalidate user cache."""
        rbac_cache.bulk_invalidate_user_cache(self.user_id)
        self._permissions = None
        self._groups = None


# Performance monitoring
class RBACPerformanceMonitor:
    """Monitor RBAC performance metrics."""

    def __init__(self):
        self.redis = get_redis_client()
        self.metrics_prefix = "rbac_metrics:"

    def record_permission_check(
        self,
        user_id: str,
        permission: str,
        duration: float,
        cached: bool,
    ):
        """Record permission check metrics."""
        timestamp = int(time.time())

        # Record timing
        timing_key = f"{self.metrics_prefix}timing:{user_id}:{permission}"
        self.redis.zadd(timing_key, {str(timestamp): duration})
        self.redis.expire(timing_key, 86400)  # 24 hours

        # Record cache hit/miss
        cache_key = f"{self.metrics_prefix}cache:{user_id}:{permission}"
        if cached:
            self.redis.hincrby(cache_key, "hits", 1)
        else:
            self.redis.hincrby(cache_key, "misses", 1)
        self.redis.expire(cache_key, 86400)  # 24 hours

    def get_permission_stats(self, user_id: str, permission: str) -> dict[str, Any]:
        """Get permission check statistics."""
        timing_key = f"{self.metrics_prefix}timing:{user_id}:{permission}"
        cache_key = f"{self.metrics_prefix}cache:{user_id}:{permission}"

        # Get timing data
        timings = self.redis.zrange(timing_key, 0, -1, withscores=True)
        if timings:
            durations = [score for _, score in timings]
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
        else:
            avg_duration = max_duration = min_duration = 0

        # Get cache data
        cache_data = self.redis.hgetall(cache_key)
        hits = int(cache_data.get("hits", 0))
        misses = int(cache_data.get("misses", 0))
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0

        return {
            "avg_duration": avg_duration,
            "max_duration": max_duration,
            "min_duration": min_duration,
            "total_checks": total,
            "cache_hits": hits,
            "cache_misses": misses,
            "cache_hit_rate": hit_rate,
        }


# Global performance monitor instance
rbac_performance_monitor = RBACPerformanceMonitor()
