# Testabdeckung Quick-Start Guide

## 🚀 Sofortige Umsetzung (Heute)

### 1. Test-Umgebung Setup

```bash
# 1. Test-Umgebungsvariablen setzen
export SECRET_KEY="test-secret-key-for-testing-only"
export DATABASE_URL="sqlite:///./test.db"
export REDIS_URL="redis://localhost:6379"
export WEAVIATE_URL="http://localhost:8080"
export TESTING="true"

# 2. Pytest-Konfiguration korrigieren
```

### 2. Pytest-Konfiguration aktualisieren

```ini
# pytest.ini
[tool:pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    api: API endpoint tests
    service: Service layer tests
    core: Core module tests
    endpoint: API endpoint tests

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
    --cov=backend.app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=json
```

### 3. Mock-Infrastruktur erstellen

```python
# tests/conftest.py
import pytest
from unittest.mock import patch, MagicMock
from backend.app.core.database import get_db
from backend.app.core.redis_client import get_redis_client

@pytest.fixture
def mock_db_session():
    """Mock database session for tests"""
    with patch('backend.app.core.database.get_db') as mock:
        session = MagicMock()
        mock.return_value = session
        yield session

@pytest.fixture
def mock_redis_client():
    """Mock Redis client for tests"""
    with patch('backend.app.core.redis_client.get_redis_client') as mock:
        redis_mock = MagicMock()
        redis_mock.get.return_value = None
        redis_mock.set.return_value = True
        redis_mock.delete.return_value = 1
        mock.return_value = redis_mock
        yield redis_mock

@pytest.fixture
def mock_weaviate_client():
    """Mock Weaviate client for tests"""
    with patch('backend.app.services.weaviate_service.weaviate_client') as mock:
        weaviate_mock = MagicMock()
        weaviate_mock.search.return_value = {"results": []}
        weaviate_mock.create_object.return_value = {"id": "test-id"}
        mock.return_value = weaviate_mock
        yield weaviate_mock

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for tests"""
    with patch('backend.app.services.ai_service.openai_client') as mock:
        openai_mock = MagicMock()
        openai_mock.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        mock.return_value = openai_mock
        yield openai_mock
```

### 4. Test-Daten-Factories erstellen

```python
# tests/factories.py
from uuid import uuid4
from backend.app.models.user import User
from backend.app.models.conversation import Conversation
from backend.app.models.knowledge import Document

class UserFactory:
    @staticmethod
    def create_user(**kwargs):
        return User(
            id=kwargs.get('id', uuid4()),
            email=kwargs.get('email', f"test{uuid4()}@example.com"),
            username=kwargs.get('username', f"testuser{uuid4()}"),
            password_hash=kwargs.get('password_hash', "hashed_password"),
            is_active=kwargs.get('is_active', True),
            role=kwargs.get('role', 'user'),
            **kwargs
        )

class ConversationFactory:
    @staticmethod
    def create_conversation(**kwargs):
        return Conversation(
            id=kwargs.get('id', uuid4()),
            title=kwargs.get('title', "Test Conversation"),
            user_id=kwargs.get('user_id', uuid4()),
            status=kwargs.get('status', 'active'),
            **kwargs
        )

class DocumentFactory:
    @staticmethod
    def create_document(**kwargs):
        return Document(
            id=kwargs.get('id', uuid4()),
            title=kwargs.get('title', "Test Document"),
            filename=kwargs.get('filename', "test.pdf"),
            file_path=kwargs.get('file_path', "/tmp/test.pdf"),
            file_size=kwargs.get('file_size', 1024),
            mime_type=kwargs.get('mime_type', "application/pdf"),
            status=kwargs.get('status', 'uploaded'),
            **kwargs
        )
```

## 🎯 Erste Tests implementieren

### 1. AI Service Tests (Höchste Priorität)

```python
# tests/unit/services/test_ai_service.py
import pytest
from unittest.mock import MagicMock
from backend.app.services.ai_service import AIService

class TestAIService:
    def test_generate_response_success(self, mock_openai_client):
        """Test successful response generation"""
        service = AIService()
        response = service.generate_response("Test prompt")
        assert response is not None
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_generate_response_error(self, mock_openai_client):
        """Test error handling in response generation"""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        service = AIService()
        
        with pytest.raises(Exception):
            service.generate_response("Test prompt")

    def test_handle_streaming_response(self, mock_openai_client):
        """Test streaming response handling"""
        service = AIService()
        # Implement streaming test
        pass
```

### 2. User Service Tests

```python
# tests/unit/services/test_user_service.py
import pytest
from backend.app.services.user_service import UserService
from tests.factories import UserFactory

class TestUserService:
    def test_create_user_success(self, mock_db_session):
        """Test successful user creation"""
        service = UserService()
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword"
        }
        
        user = service.create_user(**user_data)
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_authenticate_user_success(self, mock_db_session):
        """Test successful user authentication"""
        service = UserService()
        user = UserFactory.create_user()
        mock_db_session.query.return_value.filter.return_value.first.return_value = user
        
        result = service.authenticate_user(user.email, "password")
        assert result is not None

    def test_authenticate_user_invalid_credentials(self, mock_db_session):
        """Test authentication with invalid credentials"""
        service = UserService()
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = service.authenticate_user("invalid@example.com", "wrongpassword")
        assert result is None
```

### 3. Security Tests

```python
# tests/unit/core/test_security.py
import pytest
from backend.app.core.security import verify_password, create_access_token, verify_token

class TestSecurity:
    def test_password_hashing_and_verification(self):
        """Test password hashing and verification"""
        password = "testpassword"
        hashed = verify_password(password, password)  # This should hash first
        assert hashed is True

    def test_jwt_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        user_id = "test-user-id"
        token = create_access_token(data={"sub": user_id})
        assert token is not None
        
        payload = verify_token(token)
        assert payload["sub"] == user_id

    def test_invalid_token_verification(self):
        """Test invalid token verification"""
        with pytest.raises(Exception):
            verify_token("invalid-token")
```

## 🔧 Test-Ausführung

### Einzelne Tests ausführen

```bash
# Spezifischen Test ausführen
pytest tests/unit/services/test_ai_service.py::TestAIService::test_generate_response_success -v

# Alle Tests eines Moduls
pytest tests/unit/services/ -v

# Tests mit Coverage
pytest tests/unit/services/ --cov=backend.app.services.ai_service --cov-report=term-missing
```

### Alle Tests mit Coverage

```bash
# Vollständiger Testlauf
pytest --cov=backend.app --cov-report=html --cov-report=json --cov-report=term-missing -v

# Nur Unit-Tests
pytest -m unit --cov=backend.app --cov-report=term-missing

# Nur API-Tests
pytest -m api --cov=backend.app.api --cov-report=term-missing
```

## 📊 Coverage-Monitoring

### Coverage-Report anzeigen

```bash
# HTML-Report öffnen
open htmlcov/index.html

# Coverage-Zusammenfassung
python -c "
import json
data = json.load(open('coverage.json'))
total_lines = sum(f['summary']['num_statements'] for f in data['files'].values())
covered_lines = sum(f['summary']['covered_lines'] for f in data['files'].values())
print(f'Coverage: {covered_lines/total_lines*100:.1f}%')
"
```

### Coverage-Ziele verfolgen

```bash
# Coverage-Check Script
#!/bin/bash
COVERAGE=$(python -c "
import json
data = json.load(open('coverage.json'))
total_lines = sum(f['summary']['num_statements'] for f in data['files'].values())
covered_lines = sum(f['summary']['covered_lines'] for f in data['files'].values())
print(f'{covered_lines/total_lines*100:.1f}')
")

if (( $(echo "$COVERAGE >= 60" | bc -l) )); then
    echo "✅ Coverage: ${COVERAGE}% (Ziel erreicht)"
    exit 0
else
    echo "❌ Coverage: ${COVERAGE}% (Ziel: 60%)"
    exit 1
fi
```

## 🚨 Häufige Probleme & Lösungen

### Problem: Import-Fehler
```bash
# Lösung: PYTHONPATH setzen
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Problem: Datenbank-Verbindung
```python
# Lösung: Test-Datenbank verwenden
@pytest.fixture(scope="session")
def test_db():
    # SQLite in-memory database für Tests
    return "sqlite:///:memory:"
```

### Problem: Externe API-Calls
```python
# Lösung: Mock verwenden
@pytest.fixture(autouse=True)
def mock_external_apis():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": "test"}
        yield mock_get
```

## 📈 Nächste Schritte

### Woche 1 Checkliste
- [ ] Mock-Infrastruktur implementiert
- [ ] AI Service Tests geschrieben (80% Coverage)
- [ ] User Service Tests geschrieben (80% Coverage)
- [ ] Security Tests geschrieben (90% Coverage)
- [ ] Coverage-Monitoring eingerichtet

### Woche 2 Checkliste
- [ ] Auth Endpoint Tests (85% Coverage)
- [ ] Chat Endpoint Tests (85% Coverage)
- [ ] Knowledge Service Tests (80% Coverage)
- [ ] Integration-Tests begonnen

### Woche 3 Checkliste
- [ ] Alle kritischen Services getestet
- [ ] API-Endpoints vollständig getestet
- [ ] Performance-Tests implementiert
- [ ] Quality Gates eingerichtet

## 🎯 Erfolgsmetriken

### Kurzfristig (1 Woche)
- [ ] Testabdeckung: 44.3% → 55%
- [ ] Kritische Services: > 70% Coverage
- [ ] Fehlgeschlagene Tests: < 200

### Mittelfristig (2 Wochen)
- [ ] Testabdeckung: 55% → 65%
- [ ] Alle Services: > 75% Coverage
- [ ] Vollständige Unit-Tests

### Langfristig (4 Wochen)
- [ ] Testabdeckung: 65% → 75%
- [ ] Performance-Tests implementiert
- [ ] Security-Tests implementiert

---

**Start:** 27. Juli 2025  
**Nächste Review:** 3. August 2025  
**Verantwortlich:** Entwicklungsteam