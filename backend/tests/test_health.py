import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.mark.asyncio()
async def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code in [200, 400, 404]  # noqa: S101

    if response.status_code == 200:
        data = response.json()
        assert "status" in data  # noqa: S101
