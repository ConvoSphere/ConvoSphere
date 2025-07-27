# Quick Start: Test Coverage Verbesserung

## Sofortige Aktionen (Heute)

### 1. Import-Probleme beheben

#### Schritt 1: conftest.py reparieren
```bash
# Aktuelle Probleme identifizieren
source venv/bin/activate
python -m pytest tests/ --collect-only
```

#### Schritt 2: Fehlende Imports korrigieren
```python
# Beispiel: tests/conftest.py
# Vorher:
from app.core.redis_client import redis

# Nachher:
from backend.app.core.redis_client import redis
```

### 2. Test-Datenbank einrichten

#### SQLite für schnelle Tests (Empfohlen)
```python
# tests/conftest.py
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def test_database_url():
    """Get test database URL - SQLite for speed, PostgreSQL for compatibility"""
    # Allow override for PostgreSQL testing
    if os.getenv("TEST_USE_POSTGRESQL"):
        return "postgresql://test_user:test_password@localhost:5435/test_db"
    else:
        return "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_engine(test_database_url):
    """Create test database engine"""
    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False} if "sqlite" in test_database_url else {}
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_engine):
    """Create database session for each test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.rollback()
    session.close()
```

#### Optional: PostgreSQL für Integration-Tests
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  test-db:
    image: postgres:15
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5435:5432"
    volumes:
      - test_data:/var/lib/postgresql/data

volumes:
  test_data:
```

### 3. Erste Auth-Service Tests

#### Beispiel: backend/app/services/auth_service.py testen
```python
# tests/unit/backend/test_auth_service.py
import pytest
from unittest.mock import Mock, patch
from backend.app.services.auth_service import AuthService

class TestAuthService:
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.fixture
    def mock_user(self):
        return Mock(
            id=1,
            email="test@example.com",
            is_active=True,
            hashed_password="hashed_password"
        )
    
    def test_authenticate_user_success(self, auth_service, mock_user):
        """Test successful user authentication"""
        with patch('backend.app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            result = auth_service.authenticate_user(mock_user, "password")
            
            assert result == mock_user
            mock_verify.assert_called_once_with("password", "hashed_password")
    
    def test_authenticate_user_failure(self, auth_service, mock_user):
        """Test failed user authentication"""
        with patch('backend.app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = False
            
            result = auth_service.authenticate_user(mock_user, "wrong_password")
            
            assert result is False
    
    def test_create_access_token(self, auth_service):
        """Test access token creation"""
        token = auth_service.create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=None
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
```

## Wöchentlicher Fortschritt

### Woche 1 Checkliste
- [ ] Alle Import-Fehler behoben
- [ ] Test-Datenbank läuft
- [ ] 5 Auth-Service Tests geschrieben
- [ ] Coverage: 40%+ erreicht

### Woche 2 Checkliste
- [ ] 20+ Service Tests geschrieben
- [ ] Mock-Infrastruktur implementiert
- [ ] Coverage: 50%+ erreicht
- [ ] CI/CD Pipeline erstellt

## Praktische Tipps

### 1. Test-Daten erstellen
```python
# tests/fixtures/test_data.py
from factory import Factory, Faker
from backend.app.models.user import User

class UserFactory(Factory):
    class Meta:
        model = User
    
    email = Faker('email')
    username = Faker('user_name')
    is_active = True
```

### 2. Mock-Strategien
```python
# Externe API mocken
@patch('backend.app.services.ai_service.openai.ChatCompletion.create')
def test_ai_service_response(mock_openai):
    mock_openai.return_value = {
        'choices': [{'message': {'content': 'Test response'}}]
    }
    # Test implementation
```

### 3. Performance-Tests
```python
# tests/performance/test_api_performance.py
import pytest
import time
from backend.app.api.v1.endpoints.chat import chat_endpoint

def test_chat_response_time():
    """Test chat endpoint response time"""
    start_time = time.time()
    
    # Call chat endpoint
    response = chat_endpoint(mock_request)
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response_time < 2.0  # Should respond within 2 seconds
```

## Monitoring-Setup

### Coverage-Report automatisch generieren
```bash
# In CI/CD Pipeline
python -m pytest --cov=backend --cov-report=html --cov-report=xml
```

### Wöchentlicher Report
```python
# scripts/generate_coverage_report.py
import coverage
import json

def generate_weekly_report():
    cov = coverage.Coverage()
    cov.load()
    
    report_data = {
        'total_coverage': cov.report(),
        'module_coverage': cov.get_analysis(),
        'missing_lines': cov.get_missing(),
        'timestamp': datetime.now().isoformat()
    }
    
    with open('coverage_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)
```

## Nächste Schritte

1. **Heute**: Import-Probleme beheben
2. **Morgen**: Test-Datenbank einrichten
3. **Diese Woche**: Erste Auth-Tests schreiben
4. **Nächste Woche**: Service-Tests erweitern

## Erfolgsmetriken

- **Täglich**: Anzahl neuer Tests
- **Wöchentlich**: Coverage-Prozent
- **Monatlich**: Test-Ausführungszeit
- **Quartal**: Security-Scan-Ergebnisse