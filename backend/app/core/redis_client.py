"""
Redis client for caching and session management.

This module provides Redis connection setup, connection pooling,
and utility functions for the AI Assistant Platform.
"""

from typing import Any

import redis.asyncio as redis
from loguru import logger

from .config import get_settings

# Global Redis client instance
redis_client: redis.Redis | None = None


async def init_redis() -> redis.Redis:
    """
    Initialize Redis connection with connection pooling.

    Returns:
        redis.Redis: Redis client instance
    """
    global redis_client

    try:
        # Create Redis client with connection pooling
        redis_client = redis.from_url(
            get_settings().redis_url,
            db=get_settings().redis_db,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
            max_connections=20,
        )

        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")

        return redis_client

    except Exception as e:
        logger.error(f"Failed to initialize Redis connection: {e}")
        raise


async def get_redis() -> redis.Redis:
    """
    Get Redis client instance.

    Returns:
        redis.Redis: Redis client instance

    Raises:
        RuntimeError: If Redis is not initialized
    """
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client

    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection closed")


async def check_redis_connection() -> bool:
    """
    Check Redis connection status.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        client = await get_redis()
        await client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection check failed: {e}")
        return False


async def get_redis_info() -> dict[str, Any]:
    """
    Get Redis server information.

    Returns:
        dict: Redis server information
    """
    try:
        client = await get_redis()
        info = await client.info()

        return {
            "status": "connected" if await check_redis_connection() else "disconnected",
            "version": info.get("redis_version", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "unknown"),
            "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }
    except Exception as e:
        logger.error(f"Failed to get Redis info: {e}")
        return {"status": "error", "error": str(e)}


# Cache utility functions
async def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """
    Set cache value with expiration.

    Args:
        key: Cache key
        value: Value to cache
        expire: Expiration time in seconds (default: 1 hour)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = await get_redis()
        await client.setex(key, expire, str(value))
        return True
    except Exception as e:
        logger.error(f"Failed to set cache: {e}")
        return False


async def get_cache(key: str) -> str | None:
    """
    Get cache value.

    Args:
        key: Cache key

    Returns:
        Optional[str]: Cached value or None if not found
    """
    try:
        client = await get_redis()
        return await client.get(key)
    except Exception as e:
        logger.error(f"Failed to get cache: {e}")
        return None


async def delete_cache(key: str) -> bool:
    """
    Delete cache value.

    Args:
        key: Cache key

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = await get_redis()
        await client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Failed to delete cache: {e}")
        return False


async def clear_cache_pattern(pattern: str) -> int:
    """
    Clear cache entries matching pattern.

    Args:
        pattern: Redis pattern (e.g., "user:*")

    Returns:
        int: Number of deleted keys
    """
    try:
        client = await get_redis()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
        return len(keys)
    except Exception as e:
        logger.error(f"Failed to clear cache pattern: {e}")
        return 0
