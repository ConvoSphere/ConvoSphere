import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.main import app
except ImportError:
    from main import app

import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_login_fail():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "wrong"})
        assert response.status_code == 401 