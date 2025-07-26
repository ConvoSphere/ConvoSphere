import pytest

from backend.app.core.database import check_db_connection, get_db_info, init_db


def test_database_connection():
    """Test database connection status."""
    assert check_db_connection() is True  # noqa: S101


def test_database_info():
    """Test database info retrieval."""
    info = get_db_info()
    assert "status" in info  # noqa: S101
    assert info["status"] in ["connected", "disconnected", "error"]  # noqa: S101


def test_database_initialization():
    """Test database initialization."""
    try:
        init_db()
        assert True  # noqa: S101
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"Database initialization failed: {e}")
