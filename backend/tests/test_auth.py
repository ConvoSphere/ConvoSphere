import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.asyncio
async def test_login_fail():
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpass"},
    )
    assert response.status_code in [400, 401, 422]  # 400 for validation, 401 for auth, 422 for invalid data
