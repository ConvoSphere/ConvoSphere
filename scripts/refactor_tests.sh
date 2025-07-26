#!/bin/bash

# ChatAssistant Test Consolidation Script
# This script consolidates the test structure by moving backend tests to the main tests directory

set -e  # Exit on any error

echo "🔧 Starting Test Consolidation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the project root
if [ ! -f "REFACTORING_SUMMARY.md" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Create backup
print_status "Creating backup of current test structure..."
BACKUP_DIR="tests_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r tests "$BACKUP_DIR/"
cp -r backend/tests "$BACKUP_DIR/backend_tests"
print_success "Backup created in $BACKUP_DIR"

# Step 1: Create necessary directories
print_status "Creating test directory structure..."
mkdir -p tests/unit/backend
mkdir -p tests/integration/backend
mkdir -p tests/performance/backend
mkdir -p tests/security/backend
mkdir -p tests/e2e/backend
mkdir -p tests/blackbox/backend

# Step 2: Move backend tests
print_status "Moving backend tests to main test directory..."

# Move unit tests
if [ -d "backend/tests/unit" ]; then
    print_status "Moving unit tests..."
    cp -r backend/tests/unit/* tests/unit/backend/ 2>/dev/null || true
    print_success "Unit tests moved"
fi

# Move integration tests
if [ -d "backend/tests/integration" ]; then
    print_status "Moving integration tests..."
    cp -r backend/tests/integration/* tests/integration/backend/ 2>/dev/null || true
    print_success "Integration tests moved"
fi

# Move performance tests
if [ -d "backend/tests/performance" ]; then
    print_status "Moving performance tests..."
    cp -r backend/tests/performance/* tests/performance/backend/ 2>/dev/null || true
    print_success "Performance tests moved"
fi

# Step 3: Consolidate conftest.py files
print_status "Consolidating conftest.py files..."

# Create a new consolidated conftest.py
cat > tests/conftest_consolidated.py << 'EOF'
"""
Consolidated test configuration and fixtures for AI Assistant Platform.
This file combines fixtures from both tests/conftest.py and backend/tests/conftest.py
"""
import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from collections.abc import Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Update import paths for new test structure
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.core.database import get_db
from backend.app.models.base import Base
from backend.app.models.knowledge import Document, DocumentProcessingJob, Tag
from backend.app.models.user import User

# Import the main application
from backend.main import app

# Test configuration - Using PostgreSQL for all tests
TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5434/chatassistant_test"
TEST_REDIS_URL = "redis://localhost:6380"
TEST_WEAVIATE_URL = "http://localhost:8081"

# Test data fixtures
TEST_USER_DATA = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "role": "user",
}

TEST_ADMIN_DATA = {
    "email": "admin@example.com",
    "username": "admin",
    "password": "adminpassword123",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin",
}

TEST_ASSISTANT_DATA = {
    "name": "Test Assistant",
    "description": "A test assistant for testing purposes",
    "system_prompt": "You are a helpful test assistant.",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "is_active": True,
}

TEST_CONVERSATION_DATA = {
    "title": "Test Conversation",
    "assistant_id": 1,
    "user_id": 1,
}

TEST_MESSAGE_DATA = {
    "content": "Hello, this is a test message",
    "role": "user",
    "conversation_id": 1,
}

TEST_DOCUMENT_DATA = {
    "title": "Test Document",
    "description": "A test document for testing",
    "file_path": "/tmp/test_document.pdf",
    "file_size": 1024,
    "file_type": "pdf",
}

TEST_TOOL_DATA = {
    "name": "Test Tool",
    "description": "A test tool for testing",
    "category": "search",
    "function_name": "test_function",
    "parameters": {
        "query": {"type": "string", "description": "Search query"},
    },
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_engine():
    """Create database engine for testing."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def test_db_session_factory(test_engine):
    """Create database session factory for testing."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def test_db_session(test_db_session_factory):
    """Create a new database session for a test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = test_db_session_factory(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def override_get_db(test_db_session):
    """Override the database dependency."""
    def _override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    return _override_get_db

@pytest.fixture
def client(override_get_db):
    """Create a test client."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def async_client(override_get_db):
    """Create an async test client."""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="session", autouse=True)
def setup_redis_mock():
    """Mock Redis for testing."""
    with patch('backend.app.core.cache.redis.Redis') as mock_redis:
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance
        yield mock_redis_instance

@pytest.fixture(scope="session", autouse=True)
def setup_weaviate_mock():
    """Mock Weaviate for testing."""
    with patch('backend.app.services.weaviate_service.weaviate.Client') as mock_weaviate:
        mock_client = MagicMock()
        mock_weaviate.return_value = mock_client
        yield mock_client

@pytest.fixture
def test_user_headers(client, test_user_data):
    """Get headers for authenticated user."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    if response.status_code == 201:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}

@pytest.fixture
def test_admin_headers(client, test_admin_data):
    """Get headers for authenticated admin."""
    response = client.post("/api/v1/auth/register", json=test_admin_data)
    if response.status_code == 201:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}

@pytest.fixture
def test_user(test_db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(test_db_session):
    """Create a test admin user."""
    from backend.app.models.user import UserRole
    admin_user = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password="hashed_password",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
    )
    test_db_session.add(admin_user)
    test_db_session.commit()
    test_db_session.refresh(admin_user)
    return admin_user

@pytest.fixture
def test_assistant(test_db_session, test_user):
    """Create a test assistant."""
    from backend.app.models.assistant import Assistant
    assistant = Assistant(
        name="Test Assistant",
        description="A test assistant",
        system_prompt="You are a helpful assistant.",
        model="gpt-4",
        temperature=0.7,
        max_tokens=1000,
        is_active=True,
        user_id=test_user.id,
    )
    test_db_session.add(assistant)
    test_db_session.commit()
    test_db_session.refresh(assistant)
    return assistant

@pytest.fixture
def test_conversation(test_db_session, test_user, test_assistant):
    """Create a test conversation."""
    from backend.app.models.conversation import Conversation
    conversation = Conversation(
        title="Test Conversation",
        user_id=test_user.id,
        assistant_id=test_assistant.id,
    )
    test_db_session.add(conversation)
    test_db_session.commit()
    test_db_session.refresh(conversation)
    return conversation

@pytest.fixture
def test_message(test_db_session, test_conversation):
    """Create a test message."""
    from backend.app.models.message import Message
    message = Message(
        content="Hello, this is a test message",
        role="user",
        conversation_id=test_conversation.id,
    )
    test_db_session.add(message)
    test_db_session.commit()
    test_db_session.refresh(message)
    return message

@pytest.fixture
def test_document(test_db_session, test_user):
    """Create a test document."""
    document = Document(
        title="Test Document",
        description="A test document",
        file_path="/tmp/test_document.pdf",
        file_size=1024,
        file_type="pdf",
        user_id=test_user.id,
    )
    test_db_session.add(document)
    test_db_session.commit()
    test_db_session.refresh(document)
    return document

@pytest.fixture
def test_tool(test_db_session):
    """Create a test tool."""
    from backend.app.models.tool import Tool
    tool = Tool(
        name="Test Tool",
        description="A test tool",
        category="search",
        function_name="test_function",
        parameters={
            "query": {"type": "string", "description": "Search query"},
        },
    )
    test_db_session.add(tool)
    test_db_session.commit()
    test_db_session.refresh(tool)
    return tool

@pytest.fixture
def temp_file():
    """Create a temporary file."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"Test content")
        temp_file_path = f.name
    yield temp_file_path
    os.unlink(temp_file_path)

@pytest.fixture
def temp_pdf_file():
    """Create a temporary PDF file."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\nTest PDF content")
        temp_file_path = f.name
    yield temp_file_path
    os.unlink(temp_file_path)

@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a mock response from the LLM.",
                    "role": "assistant"
                }
            }
        ]
    }

@pytest.fixture
def mock_embedding_response():
    """Mock embedding response."""
    return {
        "data": [
            {
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dimensional vector
            }
        ]
    }

@pytest.fixture
def test_data():
    """General test data."""
    return {
        "users": [test_user_data, test_admin_data],
        "assistants": [test_assistant_data],
        "conversations": [test_conversation_data],
        "messages": [test_message_data],
        "documents": [test_document_data],
        "tools": [test_tool_data],
    }

@pytest.fixture
def performance_test_data():
    """Data for performance tests."""
    return {
        "large_text": "Lorem ipsum " * 1000,
        "many_users": [{"email": f"user{i}@example.com", "username": f"user{i}"} for i in range(100)],
        "many_documents": [{"title": f"Doc {i}", "content": f"Content {i}"} for i in range(50)],
    }

@pytest.fixture
def security_test_payloads():
    """Payloads for security tests."""
    return {
        "sql_injection": "'; DROP TABLE users; --",
        "xss": "<script>alert('XSS')</script>",
        "path_traversal": "../../../etc/passwd",
        "command_injection": "; rm -rf /",
    }

def create_test_file(content: str, extension: str = ".txt") -> str:
    """Create a test file with given content."""
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as f:
        f.write(content.encode())
        return f.name

def cleanup_test_file(file_path: str):
    """Clean up a test file."""
    if os.path.exists(file_path):
        os.unlink(file_path)
EOF

# Backup the original conftest.py
print_status "Backing up original conftest.py..."
cp tests/conftest.py tests/conftest_original.py

# Replace with consolidated version
print_status "Replacing conftest.py with consolidated version..."
mv tests/conftest_consolidated.py tests/conftest.py

# Step 4: Update pytest.ini
print_status "Updating pytest.ini..."
sed -i 's|backend/tests||g' pytest.ini
print_success "pytest.ini updated"

# Step 5: Create migration script for test imports
print_status "Creating test import migration script..."
cat > scripts/migrate_test_imports.py << 'EOF'
#!/usr/bin/env python3
"""
Script to update import paths in migrated test files.
"""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path):
    """Update import statements in a test file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update common import patterns
    replacements = [
        # Update relative imports
        (r'from \.\.', 'from backend'),
        (r'from \.', 'from backend.app'),
        
        # Update specific imports that might be broken
        (r'from app\.', 'from backend.app.'),
        (r'import app\.', 'import backend.app.'),
    ]
    
    original_content = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated imports in {file_path}")

def migrate_test_imports():
    """Migrate all test files in the tests directory."""
    tests_dir = Path("tests")
    
    for test_file in tests_dir.rglob("*.py"):
        if test_file.name.startswith("test_"):
            update_imports_in_file(test_file)

if __name__ == "__main__":
    migrate_test_imports()
EOF

chmod +x scripts/migrate_test_imports.py

# Step 6: Run the migration script
print_status "Running import migration script..."
python scripts/migrate_test_imports.py

# Step 7: Create a test runner script
print_status "Creating unified test runner..."
cat > scripts/run_tests.sh << 'EOF'
#!/bin/bash

# Unified Test Runner for ChatAssistant
# This script runs tests from the consolidated test structure

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Default values
TEST_TYPE="all"
PARALLEL=false
COVERAGE=true
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TEST_TYPE="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --type TYPE       Test type: all, unit, integration, e2e, performance, security"
            echo "  --parallel        Run tests in parallel"
            echo "  --no-coverage     Disable coverage reporting"
            echo "  --verbose         Verbose output"
            echo "  --help            Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=backend/app --cov=frontend-react/src --cov-report=term-missing --cov-report=html:htmlcov"
fi

# Select test path based on type
case $TEST_TYPE in
    "all")
        TEST_PATH="tests/"
        ;;
    "unit")
        TEST_PATH="tests/unit/"
        ;;
    "integration")
        TEST_PATH="tests/integration/"
        ;;
    "e2e")
        TEST_PATH="tests/e2e/"
        ;;
    "performance")
        TEST_PATH="tests/performance/"
        ;;
    "security")
        TEST_PATH="tests/security/"
        ;;
    "backend")
        TEST_PATH="tests/unit/backend/ tests/integration/backend/"
        ;;
    "frontend")
        TEST_PATH="tests/unit/frontend/ tests/integration/frontend/"
        ;;
    *)
        echo "Unknown test type: $TEST_TYPE"
        exit 1
        ;;
esac

print_status "Running $TEST_TYPE tests..."
print_status "Command: $PYTEST_CMD $TEST_PATH"

# Run tests
if $PYTEST_CMD $TEST_PATH; then
    print_success "All tests passed!"
else
    print_warning "Some tests failed. Check the output above."
    exit 1
fi
EOF

chmod +x scripts/run_tests.sh

# Step 8: Update documentation
print_status "Updating test documentation..."
cat > tests/README_CONSOLIDATED.md << 'EOF'
# Consolidated Test Structure

## Overview
This directory contains all tests for the ChatAssistant project, including both backend and frontend tests.

## Structure
```
tests/
├── unit/                 # Unit tests (fast, isolated)
│   ├── backend/         # Backend unit tests
│   └── frontend/        # Frontend unit tests
├── integration/         # Integration tests (component interaction)
│   ├── backend/         # Backend integration tests
│   └── frontend/        # Frontend integration tests
├── e2e/                # End-to-end tests (full workflows)
├── performance/        # Performance and load tests
├── security/           # Security and authentication tests
├── blackbox/           # Black box testing
├── fixtures/           # Test data and fixtures
├── conftest.py         # Consolidated test configuration
└── README.md           # This file
```

## Running Tests

### All Tests
```bash
./scripts/run_tests.sh
```

### Specific Test Types
```bash
# Unit tests only
./scripts/run_tests.sh --type unit

# Backend tests only
./scripts/run_tests.sh --type backend

# Integration tests only
./scripts/run_tests.sh --type integration

# Performance tests only
./scripts/run_tests.sh --type performance
```

### Options
- `--parallel`: Run tests in parallel
- `--no-coverage`: Disable coverage reporting
- `--verbose`: Verbose output

## Test Configuration
- Database: PostgreSQL (test database)
- Redis: Mocked for testing
- Weaviate: Mocked for testing
- All fixtures are available in `conftest.py`

## Writing Tests
1. Place tests in the appropriate directory based on type
2. Use fixtures from `conftest.py`
3. Follow naming convention: `test_*.py`
4. Use descriptive test names
5. Add appropriate markers for test categorization

## Migration Notes
- All backend tests have been moved from `backend/tests/` to `tests/`
- Import paths have been updated automatically
- Original test structure is backed up in `tests_backup_*`
EOF

# Step 9: Clean up old backend tests directory
print_status "Cleaning up old backend tests directory..."
if [ -d "backend/tests" ]; then
    mv backend/tests backend/tests_old
    print_warning "Old backend tests moved to backend/tests_old (can be deleted after verification)"
fi

# Step 10: Run a quick test to verify everything works
print_status "Running verification test..."
if python -m pytest tests/unit/backend/ -v --tb=short --maxfail=1; then
    print_success "Verification test passed!"
else
    print_warning "Verification test failed. Check the output above."
    print_warning "You may need to manually fix some import issues."
fi

print_success "Test consolidation completed!"
echo ""
echo "📋 Summary:"
echo "✅ Backend tests moved to tests/"
echo "✅ conftest.py consolidated"
echo "✅ pytest.ini updated"
echo "✅ Test runner script created"
echo "✅ Documentation updated"
echo "✅ Backup created in $BACKUP_DIR"
echo ""
echo "🚀 Next steps:"
echo "1. Review the changes in tests/"
echo "2. Run tests: ./scripts/run_tests.sh"
echo "3. Fix any remaining import issues"
echo "4. Delete backup when satisfied: rm -rf $BACKUP_DIR"
echo "5. Delete old backend tests: rm -rf backend/tests_old"
echo ""
echo "📚 Documentation: tests/README_CONSOLIDATED.md"