"""
Caching system for performance optimization.

This module provides a comprehensive caching system using Redis with:
- Multi-level caching (L1: Memory, L2: Redis)
- Cache invalidation strategies
- Cache warming and prefetching
- Cache analytics and monitoring
- Distributed caching support
"""

import hashlib
import json
from collections.abc import Callable
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any

from loguru import logger

from backend.app.core.config import get_settings
from backend.app.core.redis_client import get_redis


class CacheLevel(Enum):
    """Cache levels."""

    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"


class CacheStrategy(Enum):
    """Cache invalidation strategies."""

    TTL = "ttl"
    LRU = "lru"
    LFU = "lfu"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"


class CacheMetrics:
    """Cache performance metrics."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.set_operations = 0
        self.get_operations = 0
        self.delete_operations = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def reset(self):
        """Reset metrics."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.set_operations = 0
        self.get_operations = 0
        self.delete_operations = 0


class CacheEntry:
    """Cache entry with metadata."""

    def __init__(self, key: str, value: Any, ttl: int = 3600):
        self.key = key
        self.value = value
        self.created_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        self.access_count = 0
        self.ttl = ttl
        self.expires_at = self.created_at + timedelta(seconds=ttl)

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        return datetime.utcnow() > self.expires_at

    def access(self):
        """Record access to entry."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "ttl": self.ttl,
            "expires_at": self.expires_at.isoformat(),
        }


class CacheManager:
    """Advanced cache manager with multiple strategies."""

    def __init__(self):
        self.settings = get_settings()
        self.redis_client = get_redis()
        self.metrics = CacheMetrics()

        # Memory cache (L1)
        self.memory_cache: dict[str, CacheEntry] = {}
        self.memory_cache_size = getattr(self.settings, "memory_cache_size", 1000)

        # Cache configuration
        self.default_ttl = getattr(self.settings, "default_cache_ttl", 3600)
        self.enable_memory_cache = getattr(self.settings, "enable_memory_cache", True)
        self.enable_redis_cache = getattr(self.settings, "enable_redis_cache", True)

        # Cache warming
        self.warmup_enabled = getattr(self.settings, "cache_warmup_enabled", True)
        self.warmup_patterns = getattr(self.settings, "cache_warmup_patterns", [])

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with multi-level support."""
        self.metrics.get_operations += 1

        # Try L1 cache (memory)
        if self.enable_memory_cache:
            value = await self._get_from_memory(key)
            if value is not None:
                self.metrics.hits += 1
                return value

        # Try L2 cache (Redis)
        if self.enable_redis_cache:
            value = await self._get_from_redis(key)
            if value is not None:
                self.metrics.hits += 1
                # Store in L1 cache
                if self.enable_memory_cache:
                    await self._set_in_memory(key, value, self.default_ttl)
                return value

        self.metrics.misses += 1
        return default

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with multi-level support."""
        self.metrics.set_operations += 1
        ttl = ttl or self.default_ttl

        success = True

        # Set in L1 cache (memory)
        if self.enable_memory_cache:
            success &= await self._set_in_memory(key, value, ttl)

        # Set in L2 cache (Redis)
        if self.enable_redis_cache:
            success &= await self._set_in_redis(key, value, ttl)

        return success

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        self.metrics.delete_operations += 1

        success = True

        # Delete from L1 cache
        if self.enable_memory_cache:
            success &= await self._delete_from_memory(key)

        # Delete from L2 cache
        if self.enable_redis_cache:
            success &= await self._delete_from_redis(key)

        return success

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        # Check L1 cache
        if self.enable_memory_cache and key in self.memory_cache:
            entry = self.memory_cache[key]
            if not entry.is_expired():
                return True

        # Check L2 cache
        if self.enable_redis_cache:
            return await self.redis_client.exists(key)

        return False

    async def clear(self, pattern: str = "*") -> int:
        """Clear cache entries matching pattern."""
        deleted_count = 0

        # Clear L1 cache
        if self.enable_memory_cache:
            keys_to_delete = [
                k for k in self.memory_cache if self._match_pattern(k, pattern)
            ]
            for key in keys_to_delete:
                await self._delete_from_memory(key)
                deleted_count += 1

        # Clear L2 cache
        if self.enable_redis_cache:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                deleted_count += deleted

        return deleted_count

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache."""
        results = {}

        # Try L1 cache first
        if self.enable_memory_cache:
            for key in keys:
                value = await self._get_from_memory(key)
                if value is not None:
                    results[key] = value

        # Get remaining keys from L2 cache
        if self.enable_redis_cache:
            remaining_keys = [k for k in keys if k not in results]
            if remaining_keys:
                redis_values = await self.redis_client.mget(remaining_keys)
                for key, value in zip(remaining_keys, redis_values, strict=False):
                    if value is not None:
                        try:
                            parsed_value = json.loads(value)
                            results[key] = parsed_value
                            # Store in L1 cache
                            if self.enable_memory_cache:
                                await self._set_in_memory(
                                    key, parsed_value, self.default_ttl
                                )
                        except (json.JSONDecodeError, TypeError):
                            continue

        return results

    async def set_many(self, data: dict[str, Any], ttl: int = None) -> bool:
        """Set multiple values in cache."""
        ttl = ttl or self.default_ttl
        success = True

        # Set in L1 cache
        if self.enable_memory_cache:
            for key, value in data.items():
                success &= await self._set_in_memory(key, value, ttl)

        # Set in L2 cache
        if self.enable_redis_cache:
            pipeline = self.redis_client.pipeline()
            for key, value in data.items():
                try:
                    serialized_value = json.dumps(value)
                    pipeline.setex(key, ttl, serialized_value)
                except (TypeError, ValueError):
                    success = False

            try:
                await pipeline.execute()
            except Exception as e:
                logger.error(f"Failed to set multiple values in Redis: {e}")
                success = False

        return success

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in cache."""
        # Try L1 cache first
        if self.enable_memory_cache and key in self.memory_cache:
            entry = self.memory_cache[key]
            if not entry.is_expired() and isinstance(entry.value, int | float):
                entry.value += amount
                entry.access()
                return entry.value

        # Use Redis for atomic increment
        if self.enable_redis_cache:
            try:
                return await self.redis_client.incrby(key, amount)
            except Exception as e:
                logger.error(f"Failed to increment key {key}: {e}")

        return 0

    async def _get_from_memory(self, key: str) -> Any:
        """Get value from memory cache."""
        if key not in self.memory_cache:
            return None

        entry = self.memory_cache[key]

        # Check expiration
        if entry.is_expired():
            await self._delete_from_memory(key)
            return None

        # Record access
        entry.access()
        return entry.value

    async def _set_in_memory(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in memory cache."""
        try:
            # Check cache size and evict if necessary
            if len(self.memory_cache) >= self.memory_cache_size:
                await self._evict_from_memory()

            entry = CacheEntry(key, value, ttl)
            self.memory_cache[key] = entry
            return True
        except Exception as e:
            logger.error(f"Failed to set value in memory cache: {e}")
            return False

    async def _delete_from_memory(self, key: str) -> bool:
        """Delete value from memory cache."""
        try:
            if key in self.memory_cache:
                del self.memory_cache[key]
            return True
        except Exception as e:
            logger.error(f"Failed to delete from memory cache: {e}")
            return False

    async def _get_from_redis(self, key: str) -> Any:
        """Get value from Redis cache."""
        try:
            value = await self.redis_client.get(key)
            if value is not None:
                return json.loads(value)
            return None
        except (json.JSONDecodeError, TypeError, Exception) as e:
            logger.error(f"Failed to get value from Redis: {e}")
            return None

    async def _set_in_redis(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in Redis cache."""
        try:
            serialized_value = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized_value)
            return True
        except (TypeError, ValueError, Exception) as e:
            logger.error(f"Failed to set value in Redis: {e}")
            return False

    async def _delete_from_redis(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete from Redis: {e}")
            return False

    async def _evict_from_memory(self):
        """Evict entries from memory cache using LRU strategy."""
        if not self.memory_cache:
            return

        # Find least recently used entry
        lru_key = min(
            self.memory_cache.keys(), key=lambda k: self.memory_cache[k].last_accessed
        )

        # Remove expired entries first
        expired_keys = [
            key for key, entry in self.memory_cache.items() if entry.is_expired()
        ]

        if expired_keys:
            for key in expired_keys:
                del self.memory_cache[key]
                self.metrics.evictions += 1
        else:
            # Remove LRU entry
            del self.memory_cache[lru_key]
            self.metrics.evictions += 1

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern."""
        if pattern == "*":
            return True

        # Simple pattern matching (can be extended)
        return pattern in key

    async def warmup_cache(self, patterns: list[str] = None):
        """Warm up cache with frequently accessed data."""
        if not self.warmup_enabled:
            return

        patterns = patterns or self.warmup_patterns

        for pattern in patterns:
            try:
                # This would be implemented based on specific warmup strategies
                logger.info(f"Warming up cache for pattern: {pattern}")
                # Example: await self._warmup_documents(pattern)
            except Exception as e:
                logger.error(f"Cache warmup failed for pattern {pattern}: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get cache performance metrics."""
        return {
            "hits": self.metrics.hits,
            "misses": self.metrics.misses,
            "hit_rate": self.metrics.hit_rate,
            "evictions": self.metrics.evictions,
            "set_operations": self.metrics.set_operations,
            "get_operations": self.metrics.get_operations,
            "delete_operations": self.metrics.delete_operations,
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_capacity": self.memory_cache_size,
        }

    def reset_metrics(self):
        """Reset cache metrics."""
        self.metrics.reset()


class CacheDecorator:
    """Decorator for caching function results."""

    def __init__(
        self,
        ttl: int = 3600,
        key_prefix: str = "",
        key_generator: Callable = None,
        cache_manager: CacheManager = None,
    ):
        self.ttl = ttl
        self.key_prefix = key_prefix
        self.key_generator = key_generator
        self.cache_manager = cache_manager or CacheManager()

    def __call__(self, func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if self.key_generator:
                cache_key = self.key_generator(func, args, kwargs)
            else:
                cache_key = self._generate_key(func, args, kwargs)

            # Try to get from cache
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await self.cache_manager.set(cache_key, result, self.ttl)

            return result

        return wrapper

    def _generate_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function and arguments."""
        # Create a hash of function name and arguments
        key_data = {
            "func": func.__name__,
            "args": args,
            "kwargs": sorted(kwargs.items()),
        }

        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"{self.key_prefix}:{key_hash}"


# Global cache manager instance
_cache_manager: CacheManager | None = None


def get_cache_manager() -> CacheManager:
    """Get or create cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache(ttl: int = 3600, key_prefix: str = "", key_generator: Callable = None):
    """Decorator for caching function results."""
    return CacheDecorator(ttl, key_prefix, key_generator)


def cache_key_generator(func: Callable, args: tuple, kwargs: dict) -> str:
    """Default cache key generator."""
    # Use function name and first argument (usually ID) for simple cases
    if args and hasattr(args[0], "__str__"):
        return f"{func.__name__}:{args[0]}"
    return f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
