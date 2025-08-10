# Test configuration bridge for backend/tests to reuse global fixtures
from tests.conftest import *  # noqa: F401,F403

import pytest


# Alias expected fixture names in backend tests to global ones
@pytest.fixture
def db_session(test_db_session):
    return test_db_session