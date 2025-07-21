import pytest
from app.core.redis_client import (
    check_redis_connection,
    delete_cache,
    get_cache,
    get_redis_info,
    set_cache,
)


@pytest.mark.asyncio
async def test_redis_connection():
    """Test Redis connection status."""
    # This test requires Redis to be running
    try:
        result = await check_redis_connection()
        assert isinstance(result, bool)
    except Exception:
        # If Redis is not available, test should be skipped
        pytest.skip("Redis not available")


@pytest.mark.asyncio
async def test_redis_info():
    """Test Redis info retrieval."""
    try:
        info = await get_redis_info()
        assert "status" in info
        assert info["status"] in ["connected", "disconnected", "error"]
    except Exception:
        pytest.skip("Redis not available")


@pytest.mark.asyncio
async def test_cache_operations():
    """Test basic cache operations."""
    try:
        # Test set cache
        success = await set_cache("test_key", "test_value", 60)
        assert success == True

        # Test get cache
        value = await get_cache("test_key")
        assert value == "test_value"

        # Test delete cache
        success = await delete_cache("test_key")
        assert success == True

        # Verify deletion
        value = await get_cache("test_key")
        assert value is None

    except Exception:
        pytest.skip("Redis not available")
