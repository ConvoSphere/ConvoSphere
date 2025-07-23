# Automation & Quality Assurance

## Overview

This document describes the automation tools, CI/CD pipeline, and quality assurance processes used in the AI Assistant Platform.

## Continuous Integration (CI)

### GitHub Actions Workflow

The project uses GitHub Actions for automated testing and deployment:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
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
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run linting
      run: |
        flake8 backend/
        black --check backend/
        isort --check-only backend/
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

### Pre-commit Hooks

Automated code quality checks before commits:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
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
        additional_dependencies: [flake8-docstrings]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Code Quality Tools

### Linting

#### Flake8 Configuration

```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    .env,
    migrations
```

#### Black Configuration

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

### Type Checking

#### MyPy Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "fastapi.*",
    "pydantic.*",
    "sqlalchemy.*"
]
ignore_missing_imports = true
```

## Testing Automation

### Test Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Test Automation Scripts

```bash
#!/bin/bash
# scripts/run-tests.sh

set -e

echo "Running tests..."

# Run unit tests
echo "Running unit tests..."
pytest tests/ -m "not integration" -v

# Run integration tests
echo "Running integration tests..."
pytest tests/ -m "integration" -v

# Run with coverage
echo "Generating coverage report..."
pytest --cov=app --cov-report=html --cov-report=term-missing

echo "Tests completed successfully!"
```

## Security Scanning

### Bandit Security Scanner

```yaml
# .bandit
exclude_dirs: ['tests', '.venv']
skips: ['B101', 'B601']

# Run with: bandit -r backend/
```

### Safety Dependency Checker

```bash
# Check for known security vulnerabilities
safety check -r requirements.txt
```

## Performance Monitoring

### Load Testing

```python
# tests/performance/test_load.py
import asyncio
import aiohttp
import pytest

async def test_api_performance():
    """Test API performance under load."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):
            task = session.get("http://localhost:8000/health")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # Check response times
        for response in responses:
            assert response.status == 200
            assert response.headers.get('content-type') == 'application/json'
```

### Memory Profiling

```python
# scripts/profile_memory.py
import tracemalloc
import asyncio
from app.main import app

async def profile_memory():
    """Profile memory usage of the application."""
    tracemalloc.start()
    
    # Run application operations
    # ... application code ...
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    
    tracemalloc.stop()
```

## Deployment Automation

### Docker Build

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Monitoring and Alerting

### Health Checks

```python
# app/core/health.py
from fastapi import APIRouter
from app.core.database import check_db_connection
from app.core.redis_client import check_redis_connection

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check."""
    health_status = {
        "status": "healthy",
        "components": {
            "database": check_db_connection(),
            "redis": check_redis_connection(),
            "weaviate": check_weaviate_connection()
        }
    }
    
    # Check if all components are healthy
    all_healthy = all(health_status["components"].values())
    health_status["status"] = "healthy" if all_healthy else "unhealthy"
    
    return health_status
```

### Logging Configuration

```python
# app/core/logging.py
import logging
from loguru import logger
import sys

def setup_logging():
    """Setup application logging."""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="INFO"
    )
    
    # Add file handler
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level="DEBUG"
    )
    
    # Add error file handler
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        level="ERROR"
    )
```

## Quality Gates

### Pre-deployment Checks

```bash
#!/bin/bash
# scripts/pre-deploy.sh

set -e

echo "Running pre-deployment checks..."

# Run tests
echo "Running tests..."
pytest --cov=app --cov-fail-under=80

# Run security scan
echo "Running security scan..."
bandit -r backend/

# Check dependencies
echo "Checking dependencies..."
safety check -r requirements.txt

# Run type checking
echo "Running type checking..."
mypy backend/

echo "All checks passed!"
```

### Code Coverage Requirements

- **Minimum Coverage**: 80%
- **Critical Paths**: 95%
- **New Features**: 90%

## Automation Scripts

### Development Setup

```bash
#!/bin/bash
# scripts/setup-dev.sh

echo "Setting up development environment..."

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Install pre-commit hooks
pre-commit install

# Setup database
alembic upgrade head

echo "Development environment setup complete!"
```

### Database Migration

```bash
#!/bin/bash
# scripts/migrate.sh

echo "Running database migrations..."

# Create new migration
alembic revision --autogenerate -m "$1"

# Apply migrations
alembic upgrade head

echo "Migrations completed!"
```

## Best Practices

1. **Automate Everything**: Automate repetitive tasks
2. **Fail Fast**: Catch issues early in the pipeline
3. **Monitor Continuously**: Monitor application health and performance
4. **Document Changes**: Keep documentation up to date
5. **Security First**: Scan for vulnerabilities regularly
6. **Performance Testing**: Test performance under load
7. **Rollback Strategy**: Have a plan for quick rollbacks 

## 🔑 SSO-Provider-Konfiguration

Um SSO zu aktivieren, müssen folgende Umgebungsvariablen in der `.env`-Datei gesetzt werden:

### Google OAuth2
```bash
SSO_GOOGLE_ENABLED=true
SSO_GOOGLE_CLIENT_ID=your-google-client-id
SSO_GOOGLE_CLIENT_SECRET=your-google-client-secret
SSO_GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/sso/callback/google
```

### Microsoft OAuth2
```bash
SSO_MICROSOFT_ENABLED=true
SSO_MICROSOFT_CLIENT_ID=your-microsoft-client-id
SSO_MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
SSO_MICROSOFT_REDIRECT_URI=http://localhost:8000/api/v1/auth/sso/callback/microsoft
SSO_MICROSOFT_TENANT_ID=your-microsoft-tenant-id
```

### GitHub OAuth2
```bash
SSO_GITHUB_ENABLED=true
SSO_GITHUB_CLIENT_ID=your-github-client-id
SSO_GITHUB_CLIENT_SECRET=your-github-client-secret
SSO_GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/sso/callback/github
```

### SAML
```bash
SSO_SAML_ENABLED=true
SSO_SAML_METADATA_URL=https://your-idp.com/metadata
SSO_SAML_ENTITY_ID=http://localhost:8000
SSO_SAML_ACS_URL=http://localhost:8000/api/v1/auth/sso/callback/saml
SSO_SAML_CERT_FILE=./certs/saml.crt
SSO_SAML_KEY_FILE=./certs/saml.key
```

### OIDC
```bash
SSO_OIDC_ENABLED=true
SSO_OIDC_ISSUER_URL=https://your-oidc-provider.com
SSO_OIDC_CLIENT_ID=your-oidc-client-id
SSO_OIDC_CLIENT_SECRET=your-oidc-client-secret
SSO_OIDC_REDIRECT_URI=http://localhost:8000/api/v1/auth/sso/callback/oidc
```

**Wichtige Hinweise:**
- Die Redirect-URIs müssen beim jeweiligen Provider registriert werden
- Secrets und IDs sollten sicher im Deployment (z.B. als Kubernetes Secret, Docker-Env) hinterlegt werden
- Für Produktionsumgebungen HTTPS-URLs verwenden
- SAML-Zertifikate müssen im `./certs/`-Verzeichnis hinterlegt werden 