# SQLite vs PostgreSQL für Tests - Kompatibilitätsanalyse

## Aktuelle Situation

### ✅ **SQLite ist bereits konfiguriert**
- **Default Database URL**: `sqlite:///./test.db` in `config.py`
- **SQLAlchemy**: Unterstützt beide Datenbanken
- **Tests**: Können bereits mit SQLite laufen

### ⚠️ **PostgreSQL-spezifische Features identifiziert**

## 1. PostgreSQL-spezifische Imports

### Problem: UUID-Typen
```python
# In allen Models verwendet:
from sqlalchemy.dialects.postgresql import UUID
```

**Betroffene Dateien:**
- `backend/app/models/user.py`
- `backend/app/models/assistant.py`
- `backend/app/models/conversation.py`
- `backend/app/models/audit.py`
- `backend/app/models/knowledge.py`
- `backend/app/models/domain_groups.py`
- `backend/app/models/tool.py`
- `backend/app/models/permissions.py`
- `backend/app/models/abac.py`
- `backend/app/models/audit_extended.py`

### Lösung: Cross-Database UUID-Support
```python
# Statt:
from sqlalchemy.dialects.postgresql import UUID

# Verwenden:
import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.dialects.sqlite import UUID as SQLiteUUID

# Cross-database UUID field
def UUIDField():
    """Cross-database UUID field that works with both PostgreSQL and SQLite"""
    import sqlalchemy as sa
    from sqlalchemy.dialects import registry
    
    # Check if we're using PostgreSQL or SQLite
    engine_url = get_settings().database_url
    if 'postgresql' in engine_url:
        return PostgresUUID(as_uuid=True)
    else:
        return String(36)  # SQLite doesn't have native UUID type
```

## 2. PostgreSQL-spezifische Funktionen

### Problem: Backup/Restore-Funktionen
```python
# In cli.py und admin.py:
if db_url.startswith("postgresql://"):
    # PostgreSQL backup using pg_dump
    # PostgreSQL restore using psql
```

**Lösung**: Test-spezifische Backup-Funktionen für SQLite

### Problem: PostgreSQL-spezifische SQL-Features
- **JSON-Operatoren**: `->`, `->>`, `@>`
- **Array-Typen**: `ARRAY[]`
- **Full-Text-Search**: `ts_rank()`, `to_tsvector()`
- **Window-Functions**: `ROW_NUMBER()`, `LAG()`, `LEAD()`

## 3. Kompatibilitätslösungen

### Lösung 1: Conditional Imports
```python
# backend/app/models/base.py
import sqlalchemy as sa
from sqlalchemy.dialects import registry

def get_uuid_column():
    """Get appropriate UUID column type based on database"""
    engine_url = get_settings().database_url
    
    if 'postgresql' in engine_url:
        from sqlalchemy.dialects.postgresql import UUID
        return UUID(as_uuid=True)
    else:
        # SQLite fallback - use String with UUID validation
        return sa.String(36)

def get_json_column():
    """Get appropriate JSON column type based on database"""
    engine_url = get_settings().database_url
    
    if 'postgresql' in engine_url:
        from sqlalchemy.dialects.postgresql import JSONB
        return JSONB
    else:
        return sa.JSON
```

### Lösung 2: Database-Agnostic Models
```python
# backend/app/models/user.py
from .base import get_uuid_column, get_json_column

class User(Base):
    __tablename__ = "users"
    
    id = Column(get_uuid_column(), primary_key=True, default=uuid.uuid4)
    preferences = Column(get_json_column(), nullable=True)
```

### Lösung 3: Test-spezifische Konfiguration
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def test_database_url():
    """Get test database URL - SQLite for speed, PostgreSQL for compatibility"""
    import os
    
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
```

## 4. Vorteile von SQLite für Tests

### ✅ **Performance**
- **Geschwindigkeit**: 10-100x schneller als PostgreSQL
- **Setup**: Keine externe Datenbank erforderlich
- **Isolation**: Jeder Test bekommt eigene Datei

### ✅ **Einfachheit**
- **Keine Dependencies**: SQLite ist in Python enthalten
- **Keine Konfiguration**: Funktioniert out-of-the-box
- **Keine Netzwerk**: Lokale Datei-basierte Datenbank

### ✅ **CI/CD-Freundlich**
- **Docker**: Keine zusätzlichen Container nötig
- **GitHub Actions**: Funktioniert ohne Setup
- **Travis CI**: Keine externe Infrastruktur

## 5. Nachteile von SQLite für Tests

### ❌ **Feature-Kompatibilität**
- **UUID**: Kein nativer UUID-Typ
- **JSON**: Begrenzte JSON-Operatoren
- **Concurrency**: Begrenzte gleichzeitige Verbindungen
- **Full-Text-Search**: Keine erweiterten Suchfunktionen

### ❌ **Verhaltensunterschiede**
- **Constraints**: Weniger strikte Constraint-Validierung
- **Transactions**: Unterschiedliches Transaction-Verhalten
- **Indexes**: Unterschiedliche Index-Optimierungen

## 6. Empfohlene Strategie

### **Hybrid-Ansatz: SQLite + PostgreSQL**

#### **Phase 1: SQLite für Unit-Tests (Sofort)**
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=backend
    --cov-report=html
    --cov-report=term-missing
    --database-url=sqlite:///./test.db
```

#### **Phase 2: PostgreSQL für Integration-Tests (Optional)**
```python
# tests/integration/conftest.py
@pytest.fixture(scope="session")
def postgresql_engine():
    """PostgreSQL engine for integration tests"""
    if not os.getenv("TEST_USE_POSTGRESQL"):
        pytest.skip("PostgreSQL tests disabled")
    
    return create_engine("postgresql://test_user:test_password@localhost:5435/test_db")
```

#### **Phase 3: Cross-Database Models (Langfristig)**
```python
# backend/app/models/base.py
class CrossDatabaseBase:
    """Base class with cross-database compatibility"""
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(get_uuid_column(), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## 7. Implementierungsplan

### **Sofort (1-2 Tage)**
1. **SQLite-Konfiguration aktivieren**
2. **UUID-Imports anpassen**
3. **Basis-Tests mit SQLite laufen lassen**

### **Kurzfristig (1 Woche)**
1. **Cross-database UUID-Support implementieren**
2. **JSON-Field-Kompatibilität sicherstellen**
3. **Test-Fixtures für SQLite erstellen**

### **Mittelfristig (2-4 Wochen)**
1. **PostgreSQL-spezifische Features identifizieren**
2. **Alternative Implementierungen für SQLite**
3. **Integration-Tests mit PostgreSQL (optional)**

## 8. Konkrete Code-Änderungen

### **Schritt 1: UUID-Support**
```python
# backend/app/models/base.py
import uuid
from sqlalchemy import String, Column
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

def UUIDField():
    """Cross-database UUID field"""
    from backend.app.core.config import get_settings
    
    engine_url = get_settings().database_url
    if 'postgresql' in engine_url:
        return PostgresUUID(as_uuid=True)
    else:
        # SQLite fallback
        return String(36)
```

### **Schritt 2: Model-Anpassungen**
```python
# backend/app/models/user.py
from .base import UUIDField

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUIDField(), primary_key=True, default=uuid.uuid4)
    # ... rest of the model
```

### **Schritt 3: Test-Konfiguration**
```python
# tests/conftest.py
import pytest
import os

@pytest.fixture(scope="session")
def database_url():
    """Get database URL for tests"""
    return os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

@pytest.fixture(scope="session")
def engine(database_url):
    """Create test engine"""
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )
    
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
```

## 9. Fazit

### **✅ SQLite für Tests ist machbar und empfehlenswert**

**Vorteile:**
- **Schnellere Tests**: 10-100x Performance-Gewinn
- **Einfachere Setup**: Keine externe Infrastruktur
- **Bessere CI/CD**: Funktioniert überall
- **Kostengünstig**: Keine zusätzlichen Ressourcen

**Herausforderungen:**
- **UUID-Support**: Muss angepasst werden
- **Feature-Kompatibilität**: Einige PostgreSQL-Features fehlen
- **Verhaltensunterschiede**: Subtile Unterschiede möglich

**Empfehlung:**
1. **Sofort**: SQLite für Unit-Tests verwenden
2. **Optional**: PostgreSQL für Integration-Tests
3. **Langfristig**: Cross-database kompatible Models

**Risiko: Niedrig** - SQLAlchemy abstrahiert die meisten Unterschiede, und die identifizierten Probleme sind lösbar.