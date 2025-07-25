# Test Structure

This directory contains all tests for the AI Assistant Platform, organized by type and component.

## Structure

```
tests/
├── unit/                    # Unit tests
│   └── backend/            # Backend unit tests
├── integration/            # Integration tests
│   ├── backend/           # Backend integration tests
│   └── frontend/          # Frontend integration tests (future)
├── performance/           # Performance tests
│   └── backend/          # Backend performance tests
├── security/             # Security tests
│   └── backend/          # Backend security tests
├── e2e/                  # End-to-end tests
│   └── cypress/          # Cypress E2E tests
├── conftest.py           # Shared test configuration
├── pytest.ini           # Pytest configuration
└── README.md            # This file
```

## Backend Tests

Backend tests are also organized in `backend/tests/` with the same structure:

```
backend/tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
├── performance/          # Performance tests
└── security/            # Security tests
```

## Running Tests

### All Tests
```bash
pytest
```

### Specific Test Types
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Performance tests only
pytest -m performance

# Security tests only
pytest -m security

# E2E tests only
pytest -m e2e
```

### Specific Components
```bash
# Backend tests only
pytest tests/unit/backend/ tests/integration/backend/ tests/performance/backend/ tests/security/backend/
pytest backend/tests/

# Frontend tests only (when available)
pytest tests/unit/frontend/ tests/integration/frontend/
```

### Cypress E2E Tests
```bash
cd frontend-react
npm run cypress:run
```

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.database` - Database tests
- `@pytest.mark.redis` - Redis tests
- `@pytest.mark.weaviate` - Weaviate tests

## Test Configuration

- `conftest.py` - Shared fixtures and configuration
- `pytest.ini` - Pytest settings and markers
- `backend/tests/conftest.py` - Backend-specific fixtures