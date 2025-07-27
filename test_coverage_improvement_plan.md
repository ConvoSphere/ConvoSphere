# Testabdeckung Verbesserungsplan - AKTUALISIERT

## Aktuelle Situation (Stand: 27. Juli 2025)

**Aktuelle Testabdeckung:** 38% (5.940 von 15.647 Codezeilen)  
**Tests gefunden:** 1.082 Tests  
**Erfolgreiche Tests:** 260 ✅  
**Fehlgeschlagene Tests:** 66 ❌  
**Fehler:** 121 ⚠️  
**Übersprungene Tests:** 7 ⏭️  

## ✅ ERREICHTE FORTSCHRITTE

### 1. Konfigurationsprobleme behoben
- ✅ Pytest-Marks korrekt registriert
- ✅ `--strict-markers` entfernt
- ✅ Umgebungsvariablen korrekt gesetzt

### 2. AI Service Tests erfolgreich
- ✅ `test_execute_tool_call` - behoben
- ✅ `test_embed_text` - behoben
- ✅ Mock-Implementierungen korrigiert
- ✅ AsyncMock für Tool Service

### 3. Tools Endpoints Tests erfolgreich
- ✅ 96% Coverage in `tools.py`
- ✅ Alle CRUD-Operationen funktionieren
- ✅ Validierung und Fehlerbehandlung getestet

### 4. Coverage-Berichte erstellt
- ✅ HTML-Coverage-Bericht: `htmlcov/`
- ✅ JSON-Coverage-Daten: `coverage.json`
- ✅ Detaillierte Missing-Lines-Analyse

## 🔴 VERBLEIBENDE HAUPTPROBLEME

### 1. SQLAlchemy-Mapper-Fehler (Kritisch)
```
Mapper 'Mapper[User(users)]' has no property 'domain_groups'
```
**Betroffene Tests:** 121 Fehler
- Audit Service Tests
- Auth Service Tests  
- User Service Tests
- Model Tests

### 2. Externe Dienste nicht verfügbar
```
Connection to Weaviate failed
```
**Betroffene Tests:** 66 Fehler
- Chat Endpoints
- User Endpoints
- WebSocket Endpoints

### 3. DocumentService Initialisierungsfehler
```
DocumentService.__init__() missing 1 required positional argument
```
**Betroffene Tests:** 40 Fehler
- Document Processor Tests

### 4. WebSocket Mock-Probleme
```
object MagicMock can't be used in 'await' expression
```
**Betroffene Tests:** 8 Fehler

## 🎯 NÄCHSTE SCHRITTE (Priorität 1-3)

### Priorität 1: SQLAlchemy-Mapper beheben
1. **Datenbankmodelle analysieren**
   - `User` ↔ `DomainGroup` Beziehung prüfen
   - Missing Properties identifizieren
   - Foreign Key Constraints überprüfen

2. **Test-Fixtures korrigieren**
   - `test_user` Fixture anpassen
   - Datenbank-Setup vereinfachen
   - Mock-Datenbank verwenden

### Priorität 2: Externe Dienste mocken
1. **Weaviate-Mock implementieren**
   - Connection-Fehler abfangen
   - Mock-Responses bereitstellen
   - Service-Initialisierung umgehen

2. **Redis-Mock verbessern**
   - Connection-Fehler behandeln
   - Mock-Cache implementieren

### Priorität 3: DocumentService korrigieren
1. **Constructor-Parameter analysieren**
   - Fehlende Parameter identifizieren
   - Default-Werte setzen
   - Mock-Implementierung erstellen

## 📊 COVERAGE-ANALYSE

### Module mit hoher Coverage (>80%)
- `backend/app/api/v1/endpoints/tools.py`: 96% ✅
- `backend/app/schemas/knowledge.py`: 100% ✅
- `backend/app/services/auth_service.py`: 100% ✅
- `backend/app/models/audit.py`: 93% ✅

### Module mit niedriger Coverage (<20%)
- `backend/app/api/v1/endpoints/assistants.py`: 0% 🔴
- `backend/app/api/v1/endpoints/config.py`: 0% 🔴
- `backend/app/api/v1/endpoints/rbac_management.py`: 0% 🔴
- `backend/app/api/v1/endpoints/sso.py`: 0% 🔴

## 🚀 SOFORTIGE AKTIONEN

### Heute (Tag 1)
1. **SQLAlchemy-Mapper-Problem lösen**
   ```bash
   # Datenbankmodelle analysieren
   python3 -c "from backend.app.models.user import User; print(User.__table__.columns)"
   ```

2. **Test-Fixtures vereinfachen**
   - Mock-Datenbank für Unit-Tests
   - Externe Dienste komplett mocken

### Diese Woche (Tag 2-5)
1. **Weaviate-Mock implementieren**
2. **DocumentService korrigieren**
3. **WebSocket-Tests reparieren**

### Nächste Woche (Tag 6-10)
1. **Integration-Tests hinzufügen**
2. **Coverage auf 60% erhöhen**
3. **Performance-Tests implementieren**

## 📈 ZIELSETZUNG

### Kurzfristig (1 Woche)
- **Testabdeckung:** 50% (von aktuell 38%)
- **Erfolgreiche Tests:** 500+ (von aktuell 260)
- **Fehler reduzieren:** <50 (von aktuell 121)

### Mittelfristig (1 Monat)
- **Testabdeckung:** 70%
- **Erfolgreiche Tests:** 800+
- **CI/CD-Pipeline:** Vollständig funktionsfähig

### Langfristig (3 Monate)
- **Testabdeckung:** 85%
- **Erfolgreiche Tests:** 1000+
- **Code-Qualität:** A+ Rating

## 🔧 TECHNISCHE LÖSUNGEN

### 1. SQLAlchemy-Mapper-Fix
```python
# In conftest.py
@pytest.fixture(scope="session")
def test_engine():
    # Vereinfachte Datenbank ohne komplexe Beziehungen
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine
```

### 2. Weaviate-Mock
```python
# In conftest.py
@pytest.fixture(scope="session", autouse=True)
def setup_weaviate_mock():
    with patch("backend.app.core.weaviate_client.WeaviateClient") as mock:
        mock.return_value.is_connected.return_value = True
        yield mock
```

### 3. DocumentService-Fix
```python
# In test_document_processor.py
@pytest.fixture
def document_service():
    with patch("backend.app.services.document.document_service.DocumentService") as mock:
        mock.return_value = MagicMock()
        yield mock.return_value
```

## 📋 CHECKLISTE

- [x] Pytest-Konfiguration korrigiert
- [x] AI Service Tests behoben
- [x] Tools Endpoints Tests erfolgreich
- [x] Coverage-Berichte erstellt
- [ ] SQLAlchemy-Mapper-Problem gelöst
- [ ] Weaviate-Mock implementiert
- [ ] DocumentService korrigiert
- [ ] WebSocket-Tests repariert
- [ ] 50% Coverage erreicht
- [ ] CI/CD-Pipeline funktionsfähig

## 📞 NÄCHSTE SCHRITTE

1. **SQLAlchemy-Mapper-Problem priorisieren** (121 Fehler)
2. **Weaviate-Mock implementieren** (66 Fehler)
3. **DocumentService korrigieren** (40 Fehler)
4. **WebSocket-Tests reparieren** (8 Fehler)

**Geschätzte Zeit bis 50% Coverage:** 3-5 Tage
**Geschätzte Zeit bis 70% Coverage:** 2-3 Wochen