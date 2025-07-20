# Contributing Guide

Thank you for your interest in contributing to the AI Assistant Platform! This guide will help you get started with contributing to the project, from setting up your development environment to submitting pull requests.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Documentation](#documentation)
- [Community Guidelines](#community-guidelines)

## 🚀 Getting Started

### Prerequisites

Before you begin contributing, ensure you have:

- **Python 3.13+** installed
- **Git** installed and configured
- **PostgreSQL 14+** installed
- **Redis 6+** installed
- **Docker** (optional but recommended)

### Fork and Clone

1. **Fork the repository**
   - Go to [GitHub Repository](https://github.com/your-org/chatassistant)
   - Click the "Fork" button in the top right
   - This creates your own copy of the repository

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/chatassistant.git
   cd chatassistant
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/your-org/chatassistant.git
   ```

4. **Verify remotes**
   ```bash
   git remote -v
   # Should show:
   # origin    https://github.com/YOUR_USERNAME/chatassistant.git (fetch)
   # origin    https://github.com/YOUR_USERNAME/chatassistant.git (push)
   # upstream  https://github.com/your-org/chatassistant.git (fetch)
   # upstream  https://github.com/your-org/chatassistant.git (push)
   ```

## 🔧 Development Setup

### Environment Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your development settings
   ```

### Database Setup

1. **Create development database**
   ```bash
   # Connect to PostgreSQL
   sudo -u postgres psql
   
   # Create database and user
   CREATE DATABASE chatassistant_dev;
   CREATE USER chatassistant_dev WITH PASSWORD 'dev_password';
   GRANT ALL PRIVILEGES ON DATABASE chatassistant_dev TO chatassistant_dev;
   \q
   ```

2. **Run migrations**
   ```bash
   alembic upgrade head
   ```

3. **Seed development data**
   ```bash
   python scripts/seed_dev_data.py
   ```

### Service Setup

1. **Start Redis**
   ```bash
   sudo systemctl start redis-server
   # Or using Docker:
   docker run -d --name redis-dev -p 6379:6379 redis:7-alpine
   ```

2. **Start Weaviate**
   ```bash
   docker run -d \
     --name weaviate-dev \
     -p 8080:8080 \
     -e QUERY_DEFAULTS_LIMIT=25 \
     -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
     -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
     -e DEFAULT_VECTORIZER_MODULE='none' \
     -e ENABLE_MODULES='text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai' \
     -e CLUSTER_HOSTNAME='node1' \
     semitechnologies/weaviate:1.22.4
   ```

### Running the Application

1. **Start the development server**
   ```bash
   # From the backend directory
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Verify setup**
   ```bash
   # Test health endpoint
   curl http://localhost:8000/health
   
   # Test API documentation
   open http://localhost:8000/docs
   ```

## 📝 Code Style

### Python Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) and use several tools to maintain code quality:

#### Black (Code Formatter)
```bash
# Format all Python files
black .

# Format specific file
black app/api/endpoints/users.py

# Check formatting without making changes
black --check .
```

#### isort (Import Sorter)
```bash
# Sort imports in all files
isort .

# Sort imports in specific file
isort app/api/endpoints/users.py

# Check import sorting without making changes
isort --check-only .
```

#### Flake8 (Linter)
```bash
# Run linter
flake8 .

# Run with specific configuration
flake8 --config .flake8 app/
```

### Code Style Guidelines

#### Naming Conventions
```python
# Variables and functions: snake_case
user_name = "john_doe"
def get_user_by_id(user_id: str):
    pass

# Classes: PascalCase
class UserService:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# Private methods: _prefix
def _internal_helper():
    pass
```

#### Type Hints
```python
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

def get_user(user_id: str) -> Optional[User]:
    pass

def create_users(users: List[UserCreate]) -> List[User]:
    pass

def update_user_data(user_id: str, data: Dict[str, Any]) -> User:
    pass
```

#### Docstrings
```python
def create_user(user_data: UserCreate) -> User:
    """
    Create a new user in the system.
    
    Args:
        user_data: User creation data
        
    Returns:
        User: The created user object
        
    Raises:
        ValueError: If user data is invalid
        ConflictError: If user already exists
    """
    pass
```

#### Error Handling
```python
from fastapi import HTTPException
from app.core.exceptions import CustomException

def process_user_data(user_id: str) -> Dict[str, Any]:
    try:
        user = get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"user": user, "status": "success"}
    except CustomException as e:
        logger.error(f"Custom error processing user {user_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Pre-commit Hooks

We use pre-commit hooks to automatically check code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_users.py

# Run specific test function
pytest tests/test_users.py::test_create_user

# Run tests with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_api/                # API endpoint tests
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_assistants.py
├── test_services/           # Service layer tests
│   ├── test_user_service.py
│   └── test_auth_service.py
├── test_models/             # Model tests
│   └── test_user.py
└── test_integration/        # Integration tests
    └── test_database.py
```

### Writing Tests

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.models.user import User

class TestUserService:
    def test_create_user_success(self):
        """Test successful user creation."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        # Act
        user = UserService.create_user(user_data)
        
        # Assert
        assert user.email == user_data["email"]
        assert user.first_name == user_data["first_name"]
        assert user.last_name == user_data["last_name"]
        assert user.is_active is True

    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email."""
        # Arrange
        user_data = {"email": "existing@example.com", "password": "password123"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            UserService.create_user(user_data)
```

#### Integration Tests
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user_integration():
    """Test user creation through API."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "integration@example.com",
            "password": "securepassword123",
            "first_name": "Integration",
            "last_name": "Test"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "integration@example.com"
    assert "id" in data
```

#### Test Fixtures
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.user import User

@pytest.fixture
def test_db():
    """Create test database."""
    engine = create_engine("sqlite:///./test.db")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Create test client with test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_user(test_db):
    """Create test user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user
```

### Test Coverage

We aim for at least 90% test coverage. To check coverage:

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update your fork**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make your changes**
   - Write your code following the style guidelines
   - Add tests for new functionality
   - Update documentation if needed

4. **Run tests and checks**
   ```bash
   # Run all tests
   pytest
   
   # Run pre-commit hooks
   pre-commit run --all-files
   
   # Check code formatting
   black --check .
   isort --check-only .
   flake8 .
   ```

### Submitting the PR

1. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add user profile management"
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "Compare & pull request"
   - Fill out the PR template

### PR Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows the style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] No new warnings generated
- [ ] Tests added that prove fix is effective or feature works

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Additional Notes
Any additional information that reviewers should know.
```

### PR Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code quality checks pass
   - Coverage requirements met

2. **Code Review**
   - At least one maintainer reviews
   - Address any feedback
   - Make requested changes

3. **Merge**
   - PR approved and merged
   - Branch deleted
   - Changes deployed

## 🐛 Issue Reporting

### Before Reporting

1. **Check existing issues**
   - Search for similar issues
   - Check if it's already been reported

2. **Try to reproduce**
   - Test on latest version
   - Check if it's environment-specific

### Issue Template

```markdown
## Bug Report

### Description
Clear and concise description of the bug.

### Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

### Expected Behavior
What you expected to happen.

### Actual Behavior
What actually happened.

### Environment
- OS: [e.g. Ubuntu 20.04]
- Python Version: [e.g. 3.13.0]
- Database: [e.g. PostgreSQL 15]
- Redis: [e.g. 7.0]

### Additional Context
Any other context about the problem.

### Screenshots
If applicable, add screenshots to help explain your problem.
```

## 📚 Documentation

### Documentation Standards

1. **Code Documentation**
   - Use docstrings for all functions and classes
   - Follow Google or NumPy docstring format
   - Include type hints

2. **API Documentation**
   - Use OpenAPI/Swagger annotations
   - Provide clear examples
   - Document all parameters and responses

3. **README Updates**
   - Update README for new features
   - Include usage examples
   - Update installation instructions

### Documentation Structure

```
docs/
├── getting-started/          # Getting started guides
├── api/                     # API documentation
├── development/             # Development guides
├── deployment/              # Deployment guides
├── features/                # Feature documentation
└── project/                 # Project information
```

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative and open to feedback
- Focus on what is best for the community
- Show empathy towards other community members

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord**: For real-time chat and community support

### Recognition

Contributors are recognized in several ways:

- **Contributors list** in README
- **Release notes** for significant contributions
- **GitHub profile** shows contribution activity

## 🎯 Getting Help

### Resources

- **Documentation**: [docs/](https://github.com/your-org/chatassistant/docs)
- **API Reference**: [docs/api/](https://github.com/your-org/chatassistant/docs/api)
- **Issues**: [GitHub Issues](https://github.com/your-org/chatassistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/chatassistant/discussions)

### Asking for Help

When asking for help:

1. **Be specific** about your problem
2. **Include relevant code** and error messages
3. **Describe what you've tried**
4. **Provide environment details**

### Mentorship

New contributors can:

- Ask for help in GitHub Discussions
- Request a mentor for guidance
- Join community events and workshops

---

<div align="center">

**Ready to contribute?** Start by [forking the repository](https://github.com/your-org/chatassistant/fork)!

</div> 