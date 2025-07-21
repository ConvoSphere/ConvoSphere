import pytest
from httpx import AsyncClient

from backend.main import app


@pytest.mark.asyncio
async def test_login_fail():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/login",
            json={"email": "wrong@example.com", "password": "wrongpass"},
        )
    assert response.status_code == 401
