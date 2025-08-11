# Test configuration bridge for backend/tests to reuse global fixtures
from tests.conftest import *  # noqa: F401,F403

import pytest
from fastapi.testclient import TestClient

from backend.app.core.database import get_db
from backend.main import app


# Alias expected fixture names in backend tests to global ones
@pytest.fixture
def db_session(test_db_session):
    return test_db_session


@pytest.fixture
def client(db_session):
    """Create a TestClient that uses the same db_session fixture."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()