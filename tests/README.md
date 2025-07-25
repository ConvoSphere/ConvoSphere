# Test Structure

This directory contains all tests for the AI Assistant Platform, organized by type and component.

## Structure

```
tests/
├── unit/                    # Unit tests
│   ├── backend/            # Backend unit tests
│   └── frontend/           # Frontend unit tests
├── integration/            # Integration tests
│   ├── backend/           # Backend integration tests
│   └── frontend/          # Frontend integration tests
├── performance/           # Performance tests
│   └── backend/          # Backend performance tests
├── security/             # Security tests
│   └── backend/          # Backend security tests
├── e2e/                  # End-to-end tests
│   └── cypress/          # Cypress E2E tests
├── conftest.py           # Shared test configuration
├── pytest.ini           # Pytest configuration
├── vitest.config.ts      # Vitest configuration for frontend
├── setup.ts              # Frontend test setup
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
# Backend tests
pytest

# Frontend tests
cd frontend-react
npm run test:unit
npm run test:integration
```

### Specific Test Types
```bash
# Backend tests by type
pytest -m unit
pytest -m integration
pytest -m performance
pytest -m security
pytest -m e2e

# Frontend tests by type
npm run test:unit
npm run test:integration
```

### Specific Components
```bash
# Backend tests only
pytest tests/unit/backend/ tests/integration/backend/ tests/performance/backend/ tests/security/backend/
pytest backend/tests/

# Frontend tests only
npm run test:unit
npm run test:integration
```

### Cypress E2E Tests
```bash
cd frontend-react
npm run cypress:run
```

### Performance Tests
```bash
# Fast performance tests (included in CI)
pytest -m "performance and not slow"

# All performance tests (separate workflow)
pytest -m performance
```

## Test Markers

### Backend Markers
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

### Frontend Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests

## CI/CD Integration

### Main CI/CD Pipeline
The main pipeline runs:
- Unit tests
- Integration tests
- Security tests
- Fast performance tests (excluding slow tests)

### Performance Tests Pipeline
A separate pipeline runs:
- All performance tests (including slow tests)
- Load tests
- Memory and CPU usage tests
- Runs daily at 2 AM UTC

### Test Execution Order
1. **Unit Tests** - Fast, isolated tests
2. **Integration Tests** - Component interaction tests
3. **Security Tests** - Security vulnerability tests
4. **Performance Tests** - Performance and load tests
5. **E2E Tests** - Full application flow tests

## Test Configuration

### Backend Configuration
- `conftest.py` - Shared fixtures and configuration
- `pytest.ini` - Pytest settings and markers
- `backend/tests/conftest.py` - Backend-specific fixtures

### Frontend Configuration
- `vitest.config.ts` - Vitest configuration
- `setup.ts` - Test environment setup
- `frontend-react/package.json` - Test scripts

## Coverage Reports

### Backend Coverage
```bash
pytest --cov=backend --cov-report=html --cov-report=term-missing
```

### Frontend Coverage
```bash
cd frontend-react
npm run test:coverage
```

## Best Practices

### Writing Tests
1. **Use descriptive test names** - Test names should clearly describe what is being tested
2. **Follow AAA pattern** - Arrange, Act, Assert
3. **Test one thing at a time** - Each test should focus on a single behavior
4. **Use appropriate markers** - Mark tests with the correct category
5. **Mock external dependencies** - Don't rely on external services in unit tests

### Test Organization
1. **Group related tests** - Use describe blocks to organize related tests
2. **Use fixtures** - Share setup code between tests
3. **Keep tests independent** - Tests should not depend on each other
4. **Clean up after tests** - Use teardown functions to clean up state

### Performance Considerations
1. **Run fast tests first** - Unit tests should run quickly
2. **Use test databases** - Don't use production databases for testing
3. **Mock heavy operations** - Mock database calls, API calls, etc.
4. **Use test factories** - Create test data efficiently

## Troubleshooting

### Common Issues
1. **Import errors** - Make sure test paths are correct
2. **Database connection issues** - Check test database configuration
3. **Mock issues** - Ensure mocks are properly set up
4. **Async test issues** - Use appropriate async/await patterns

### Debugging Tests
```bash
# Run tests with verbose output
pytest -v

# Run specific test with debug output
pytest -s tests/unit/backend/test_auth.py::test_login

# Run tests with coverage and stop on first failure
pytest --cov=backend --tb=short -x
```