"""
Redis client for caching and session management.

This module provides Redis connection setup, connection pooling,
and utility functions for the AI Assistant Platform with graceful degradation.
"""

import asyncio
from typing import Any

import redis.asyncio as redis
from loguru import logger

from .config import get_settings

# Global Redis client instance
redis_client: redis.Redis | None = None
redis_available: bool = False
redis_connection_pool: redis.ConnectionPool | None = None


class RedisConnectionError(Exception):
    """Custom exception for Redis connection errors."""



async def init_redis() -> redis.Redis | None:
    """
    Initialize Redis connection with connection pooling and graceful degradation.

    Returns:
        Optional[redis.Redis]: Redis client instance or None if unavailable
    """
    global redis_client, redis_available, redis_connection_pool

    try:
        settings = get_settings()

        # Create connection pool with robust configuration
        redis_connection_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            db=settings.redis_db,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=10,
            socket_timeout=10,
            retry_on_timeout=True,
            health_check_interval=30,
            max_connections=20,
        )

        # Create Redis client
        redis_client = redis.Redis(connection_pool=redis_connection_pool)

        # Test connection with timeout
        try:
            await asyncio.wait_for(redis_client.ping(), timeout=5.0)
            redis_available = True
            logger.info("Redis connection established successfully")
            return redis_client
        except TimeoutError:
            logger.warning("Redis connection timeout during ping test")
            redis_available = False
            return None
        except Exception as e:
            logger.warning(f"Redis ping failed: {e}")
            redis_available = False
            return None

    except Exception as e:
        logger.warning(f"Failed to initialize Redis connection: {e}")
        redis_available = False
        return None


async def get_redis() -> redis.Redis | None:
    """
    Get Redis client instance with graceful degradation.

    Returns:
        Optional[redis.Redis]: Redis client instance or None if unavailable
    """
    global redis_client

    if redis_client is None:
        return None

    try:
        # Quick health check
        await asyncio.wait_for(redis_client.ping(), timeout=1.0)
        return redis_client
    except Exception:
        return None


async def close_redis() -> None:
    """Close Redis connection gracefully."""
    global redis_client, redis_available, redis_connection_pool

    try:
        if redis_client:
            await redis_client.close()
        if redis_connection_pool:
            await redis_connection_pool.disconnect()
        redis_client = None
        redis_available = False
        logger.info("Redis connection closed gracefully")
    except Exception as e:
        logger.warning(f"Error during Redis shutdown: {e}")


async def check_redis_connection() -> bool:
    """
    Check Redis connection status with timeout.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        # Try to create a direct connection for health check
        settings = get_settings()
        test_client = redis.from_url(
            settings.redis_url,
            db=settings.redis_db,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )

        await asyncio.wait_for(test_client.ping(), timeout=2.0)
        await test_client.close()
        return True
    except Exception as e:
        logger.debug(f"Redis connection check failed: {e}")
        return False


async def get_redis_info() -> dict[str, Any]:
    """
    Get Redis server information with graceful degradation.

    Returns:
        dict: Redis server information or error status
    """
    try:
        # Try to create a direct connection for info
        settings = get_settings()
        test_client = redis.from_url(
            settings.redis_url,
            db=settings.redis_db,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

        info = await asyncio.wait_for(test_client.info(), timeout=5.0)
        await test_client.close()

        return {
            "status": "connected",
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


def is_redis_available() -> bool:
    """
    Check if Redis is available without async call.

    Returns:
        bool: True if Redis is available, False otherwise
    """
    return redis_available


# Cache utility functions with graceful degradation
async def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """
    Set cache value with expiration and graceful degradation.

    Args:
        key: Cache key
        value: Value to cache
        expire: Expiration time in seconds (default: 1 hour)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = await get_redis()
        if client is None:
            return False

        await asyncio.wait_for(client.setex(key, expire, str(value)), timeout=5.0)
        return True
    except Exception as e:
        logger.debug(f"Failed to set cache: {e}")
        return False


async def get_cache(key: str) -> str | None:
    """
    Get cache value with graceful degradation.

    Args:
        key: Cache key

    Returns:
        Optional[str]: Cached value or None if not found/unavailable
    """
    try:
        client = await get_redis()
        if client is None:
            return None

        return await asyncio.wait_for(client.get(key), timeout=5.0)
    except Exception as e:
        logger.debug(f"Failed to get cache: {e}")
        return None


async def delete_cache(key: str) -> bool:
    """
    Delete cache value with graceful degradation.

    Args:
        key: Cache key

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = await get_redis()
        if client is None:
            return False

        await asyncio.wait_for(client.delete(key), timeout=5.0)
        return True
    except Exception as e:
        logger.debug(f"Failed to delete cache: {e}")
        return False


async def clear_cache_pattern(pattern: str) -> int:
    """
    Clear cache entries matching pattern with graceful degradation.

    Args:
        pattern: Redis pattern (e.g., "user:*")

    Returns:
        int: Number of deleted keys
    """
    try:
        client = await get_redis()
        if client is None:
            return 0

        keys = await asyncio.wait_for(client.keys(pattern), timeout=10.0)
        if keys:
            await asyncio.wait_for(client.delete(*keys), timeout=10.0)
        return len(keys)
    except Exception as e:
        logger.debug(f"Failed to clear cache pattern: {e}")
        return 0


# Token blacklist functions with graceful degradation
async def add_to_blacklist(token: str, expires_at: int) -> bool:
    """
    Add token to blacklist with graceful degradation.

    Args:
        token: JWT token to blacklist
        expires_at: Expiration timestamp

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = await get_redis()
        if client is None:
            return False

        await asyncio.wait_for(
            client.setex(f"blacklist:{token}", expires_at, "1"), timeout=5.0,
        )
        return True
    except Exception as e:
        logger.debug(f"Failed to add token to blacklist: {e}")
        return False


async def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted with graceful degradation.

    Args:
        token: JWT token to check

    Returns:
        bool: True if token is blacklisted, False otherwise
    """
    try:
        client = await get_redis()
        if client is None:
            return False

        result = await asyncio.wait_for(
            client.exists(f"blacklist:{token}"), timeout=2.0,
        )
        return bool(result)
    except Exception as e:
        logger.debug(f"Failed to check token blacklist: {e}")
        return False
