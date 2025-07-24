# Testing Guide

This guide covers the testing strategy and practices for the AI Chat Application.

## Testing Strategy

Our testing approach follows the testing pyramid with multiple layers:

- **Unit Tests**: Fast, isolated tests for individual functions and classes
- **Integration Tests**: Tests for component interactions and API endpoints
- **End-to-End Tests**: Full application workflow tests
- **Performance Tests**: Load and stress testing

## Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
├── fixtures/      # Test data and fixtures
└── conftest.py    # Pytest configuration
```

## Running Tests

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test -- --testPathPattern=Login.test.js
```

### End-to-End Tests

```bash
# Run E2E tests
npm run test:e2e

# Run E2E tests in headless mode
npm run test:e2e:headless
```

## Test Configuration

### Backend Test Configuration

Create a `test.env` file for test-specific environment variables:

```env
DATABASE_URL=postgresql://test_user:test_password@localhost:5432/ai_chat_app_test
REDIS_URL=redis://localhost:6379/1
SECRET_KEY=test-secret-key
JWT_SECRET_KEY=test-jwt-secret-key
```

### Pytest Configuration

The `pytest.ini` file configures test behavior:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

## Writing Tests

### Backend Unit Tests

```python
import pytest
from app.models.user import User
from app.services.auth import AuthService

class TestAuthService:
    def test_create_user(self):
        """Test user creation"""
        auth_service = AuthService()
        user_data = {
            "email": "test@example.com",
            "password": "securepassword123"
        }
        
        user = auth_service.create_user(user_data)
        
        assert user.email == user_data["email"]
        assert user.is_active is True
        assert user.verify_password(user_data["password"])

    def test_authenticate_user_valid_credentials(self):
        """Test successful authentication"""
        auth_service = AuthService()
        user_data = {
            "email": "test@example.com",
            "password": "securepassword123"
        }
        
        user = auth_service.create_user(user_data)
        authenticated_user = auth_service.authenticate(
            user_data["email"], 
            user_data["password"]
        )
        
        assert authenticated_user == user

    def test_authenticate_user_invalid_credentials(self):
        """Test failed authentication"""
        auth_service = AuthService()
        user_data = {
            "email": "test@example.com",
            "password": "securepassword123"
        }
        
        auth_service.create_user(user_data)
        authenticated_user = auth_service.authenticate(
            user_data["email"], 
            "wrongpassword"
        )
        
        assert authenticated_user is None
```

### API Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuthAPI:
    def test_register_user(self):
        """Test user registration endpoint"""
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "password" not in data

    def test_login_user(self):
        """Test user login endpoint"""
        # First register a user
        user_data = {
            "email": "loginuser@example.com",
            "password": "securepassword123",
            "full_name": "Login User"
        }
        client.post("/api/auth/register", json=user_data)
        
        # Then login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
```

### Frontend Unit Tests

```javascript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../components/Login';

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Login Component', () => {
  test('renders login form', () => {
    renderWithRouter(<Login />);
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  test('handles form submission', async () => {
    const mockOnSubmit = jest.fn();
    renderWithRouter(<Login onSubmit={mockOnSubmit} />);
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    expect(mockOnSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    });
  });
});
```

## Test Data Management

### Fixtures

Create reusable test data in `tests/fixtures/`:

```python
# tests/fixtures/users.py
import pytest
from app.models.user import User

@pytest.fixture
def sample_user():
    return {
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User"
    }

@pytest.fixture
def admin_user():
    return {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "full_name": "Admin User",
        "is_admin": True
    }
```

### Database Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from app.dependencies import get_db

# Test database
SQLALCHEMY_DATABASE_URL = "postgresql://test_user:test_password@localhost:5432/ai_chat_app_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()
```

## Performance Testing

### Load Testing

```python
# tests/performance/test_load.py
import asyncio
import aiohttp
import time

async def test_api_load():
    """Test API performance under load"""
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(100):
            task = session.get('http://localhost:8000/api/health')
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify all requests succeeded
        success_count = sum(1 for r in responses if r.status == 200)
        assert success_count == 100
        
        # Verify response time is acceptable
        assert duration < 10.0  # Should complete within 10 seconds
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: ai_chat_app_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run backend tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/ai_chat_app_test
        REDIS_URL: redis://localhost:6379/1
        SECRET_KEY: test-secret-key
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Descriptive Names**: Use clear, descriptive test names that explain what is being tested
3. **Arrange-Act-Assert**: Structure tests with clear sections for setup, execution, and verification
4. **Mock External Dependencies**: Use mocks for external services and APIs
5. **Test Edge Cases**: Include tests for error conditions and boundary cases
6. **Maintain Test Data**: Keep test data clean and minimal
7. **Fast Execution**: Keep tests fast to encourage frequent execution

## Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **Critical Paths**: 100% coverage

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure test database is running and accessible
2. **Environment Variables**: Verify test environment variables are set correctly
3. **Dependencies**: Make sure all test dependencies are installed
4. **Async Tests**: Use `pytest-asyncio` for testing async functions

### Debugging Tests

```bash
# Run tests with debug output
pytest -s -v

# Run specific test with debugger
pytest -s --pdb tests/test_auth.py::TestAuthService::test_create_user

# Run tests with coverage and show missing lines
pytest --cov=app --cov-report=term-missing
```