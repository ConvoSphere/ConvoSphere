import pytest
from app.core.database import check_db_connection, get_db_info, init_db

def test_database_connection():
    """Test database connection status."""
    assert check_db_connection() == True

def test_database_info():
    """Test database info retrieval."""
    info = get_db_info()
    assert "status" in info
    assert info["status"] in ["connected", "disconnected", "error"]

def test_database_initialization():
    """Test database initialization."""
    try:
        init_db()
        assert True  # If no exception, initialization succeeded
    except Exception as e:
        pytest.fail(f"Database initialization failed: {e}") 