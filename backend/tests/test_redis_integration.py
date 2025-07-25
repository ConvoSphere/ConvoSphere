"""
Tests for Redis integration with graceful degradation.

This module tests the robust Redis client implementation including
connection handling, graceful degradation, and error scenarios.
"""

from unittest.mock import AsyncMock, patch

import pytest
from app.core.redis_client import (
    add_to_blacklist,
    check_redis_connection,
    close_redis,
    delete_cache,
    get_cache,
    get_redis,
    get_redis_info,
    init_redis,
    is_redis_available,
    is_token_blacklisted,
    set_cache,
)


class TestRedisIntegration:
    """Test Redis integration with graceful degradation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # Reset global state before each test


    @pytest.mark.asyncio
    async def test_init_redis_success(self):
        """Test successful Redis initialization."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url") as mock_pool,
        ):
            result = await init_redis()

            assert result is not None
            assert is_redis_available() is True
            mock_pool.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_redis_connection_failure(self):
        """Test Redis initialization with connection failure."""
        with patch(
            "app.core.redis_client.redis.ConnectionPool.from_url",
            side_effect=Exception("Connection failed"),
        ):
            result = await init_redis()

            assert result is None
            assert is_redis_available() is False

    @pytest.mark.asyncio
    async def test_init_redis_ping_timeout(self):
        """Test Redis initialization with ping timeout."""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Timeout")

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            result = await init_redis()

            assert result is None
            assert is_redis_available() is False

    @pytest.mark.asyncio
    async def test_get_redis_when_available(self):
        """Test getting Redis client when available."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            result = await get_redis()

            assert result is not None

    @pytest.mark.asyncio
    async def test_get_redis_when_unavailable(self):
        """Test getting Redis client when unavailable."""
        result = await get_redis()
        assert result is None

    @pytest.mark.asyncio
    async def test_get_redis_health_check_failure(self):
        """Test getting Redis client when health check fails."""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Health check failed")

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            result = await get_redis()

            assert result is None
            assert is_redis_available() is False

    @pytest.mark.asyncio
    async def test_check_redis_connection_success(self):
        """Test Redis connection check success."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            result = await check_redis_connection()

            assert result is True

    @pytest.mark.asyncio
    async def test_check_redis_connection_failure(self):
        """Test Redis connection check failure."""
        result = await check_redis_connection()
        assert result is False

    @pytest.mark.asyncio
    async def test_get_redis_info_when_available(self):
        """Test getting Redis info when available."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.info.return_value = {
            "redis_version": "7.0.0",
            "connected_clients": 1,
            "used_memory_human": "1.0M",
            "uptime_in_seconds": 3600,
            "keyspace_hits": 100,
            "keyspace_misses": 10,
        }

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            result = await get_redis_info()

            assert result["status"] == "connected"
            assert result["version"] == "7.0.0"

    @pytest.mark.asyncio
    async def test_get_redis_info_when_unavailable(self):
        """Test getting Redis info when unavailable."""
        result = await get_redis_info()
        assert result["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_set_cache_success(self):
        """Test setting cache successfully."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.setex.return_value = True

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            result = await set_cache("test_key", "test_value")

            assert result is True
            mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_cache_when_unavailable(self):
        """Test setting cache when Redis unavailable."""
        result = await set_cache("test_key", "test_value")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_cache_success(self):
        """Test getting cache successfully."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = "test_value"

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            result = await get_cache("test_key")

            assert result == "test_value"

    @pytest.mark.asyncio
    async def test_get_cache_when_unavailable(self):
        """Test getting cache when Redis unavailable."""
        result = await get_cache("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_cache_success(self):
        """Test deleting cache successfully."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.delete.return_value = 1

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            result = await delete_cache("test_key")

            assert result is True

    @pytest.mark.asyncio
    async def test_delete_cache_when_unavailable(self):
        """Test deleting cache when Redis unavailable."""
        result = await delete_cache("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_add_to_blacklist_success(self):
        """Test adding token to blacklist successfully."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.setex.return_value = True

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            result = await add_to_blacklist("test_token", 3600)

            assert result is True
            mock_redis.setex.assert_called_once_with("blacklist:test_token", 3600, "1")

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_success(self):
        """Test checking token blacklist successfully."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.exists.return_value = 1

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            result = await is_token_blacklisted("test_token")

            assert result is True
            mock_redis.exists.assert_called_once_with("blacklist:test_token")

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_not_found(self):
        """Test checking token blacklist when token not found."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.exists.return_value = 0

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            result = await is_token_blacklisted("test_token")

            assert result is False

    @pytest.mark.asyncio
    async def test_close_redis_success(self):
        """Test closing Redis connection successfully."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            await init_redis()
            await close_redis()

            assert is_redis_available() is False

    @pytest.mark.asyncio
    async def test_graceful_degradation_pattern(self):
        """Test graceful degradation pattern."""
        # Test that application continues to work without Redis
        assert is_redis_available() is False

        # Cache operations should return False/None but not raise exceptions
        assert await set_cache("key", "value") is False
        assert await get_cache("key") is None
        assert await delete_cache("key") is False
        assert await add_to_blacklist("token", 3600) is False
        assert await is_token_blacklisted("token") is False

        # Connection check should return False
        assert await check_redis_connection() is False

        # Info should return unavailable status
        info = await get_redis_info()
        assert info["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_redis_recovery_pattern(self):
        """Test Redis recovery pattern."""
        # Start with Redis unavailable
        assert is_redis_available() is False

        # Simulate Redis becoming available
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True

        with (
            patch("app.core.redis_client.redis.Redis", return_value=mock_redis),
            patch("app.core.redis_client.redis.ConnectionPool.from_url"),
        ):
            # Re-initialize Redis
            result = await init_redis()

            assert result is not None
            assert is_redis_available() is True

            # Operations should work again
            assert await set_cache("key", "value") is True
            assert await get_cache("key") == "value"
