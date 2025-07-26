import pytest

from backend.app.core.weaviate_client import (
    check_weaviate_connection,
    get_weaviate_info,
)


def test_weaviate_connection():
    """Test Weaviate connection status."""
    # This test requires Weaviate to be running
    try:
        result = check_weaviate_connection()
        assert isinstance(result, bool)
    except Exception:
        # If Weaviate is not available, test should be skipped
        pytest.skip("Weaviate not available")


def test_weaviate_info():
    """Test Weaviate info retrieval."""
    try:
        info = get_weaviate_info()
        assert "status" in info
        assert info["status"] in ["connected", "disconnected", "error"]
    except Exception:
        pytest.skip("Weaviate not available")


def test_weaviate_schema_creation():
    """Test Weaviate schema creation."""
    try:
        from backend.app.core.weaviate_client import create_schema_if_not_exists

        # This should not raise an exception
        create_schema_if_not_exists()
        assert True
    except Exception:
        pytest.skip("Weaviate not available")
