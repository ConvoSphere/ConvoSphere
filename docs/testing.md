# Testing Documentation

## Overview

The AI Assistant Platform uses automated testing to ensure code quality, stability, and security. The test suite covers unit tests, integration tests, and end-to-end API tests for both backend and frontend.

## Test Strategy

- **Unit Tests:** Test isolated functions, services, and models.
- **Integration Tests:** Test the interaction between components (e.g., API endpoints with database/Redis/Weaviate).
- **End-to-End Tests:** Test full user flows and API endpoints.
- **Mocking:** External dependencies (e.g., Redis, Weaviate) are mocked for isolation.
- **Coverage:** 100% for implemented features (see `project/status.md`).

## Running Tests (Backend)

1. Install dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```
2. Run all tests:
   ```bash
   pytest
   ```
3. Run with coverage:
   ```bash
   pytest --cov=app
   ```

## Running Tests (Frontend)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run all tests:
   ```bash
   pytest
   ```

## Example: Endpoint Test (Backend)

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_endpoints(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

## Test Files
- Backend: `backend/tests/` (z.B. `test_endpoints.py`, `test_services.py`)
- Frontend: `frontend/tests/` (z.B. `test_pages.py`, `test_services.py`)

## Continuous Integration
- Tests werden automatisch in der CI/CD-Pipeline ausgeführt (geplant).

## Further Reading
- Siehe auch: `project/status.md` für aktuelle Testabdeckung und Teststrategie.
