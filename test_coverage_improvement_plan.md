# Testabdeckung Verbesserungsplan

## Aktuelle Situation

**Datum:** 27. Juli 2025  
**Aktuelle Testabdeckung:** 44.3% (7.021 von 15.852 Codezeilen)  
**Gesamte Tests:** 1.082 Tests gefunden  
**Erfolgreiche Tests:** 410  
**Fehlgeschlagene Tests:** 263  
**Fehler:** 407  

## Hauptprobleme identifiziert

### 1. Externe Dienste nicht verfügbar
- **Weaviate:** Connection refused (localhost:8080)
- **Redis:** Connection refused (localhost:6379)
- **HTTP-Server:** Für Blackbox-Tests nicht gestartet

### 2. Konfigurationsprobleme
- Fehlende Umgebungsvariablen
- Pytest-Marks nicht registriert
- DocumentService Initialisierungsfehler

### 3. Teststruktur-Probleme
- AsyncClient Konfigurationsfehler
- Fehlende Mock-Implementierungen
- Unvollständige Test-Fixtures

## Umsetzungsplan

### Phase 1: Infrastruktur & Konfiguration (Woche 1-2)

#### 1.1 Test-Umgebung Setup
- [ ] Docker-Compose für Test-Dienste erstellen
- [ ] Redis-Mock für Tests implementieren
- [ ] Weaviate-Mock für Tests implementieren
- [ ] Test-Datenbank Setup automatisieren

#### 1.2 Konfiguration korrigieren
- [ ] Pytest-Marks in `pytest.ini` registrieren
- [ ] Test-Umgebungsvariablen zentralisieren
- [ ] `.env.test` Datei erstellen
- [ ] Test-Fixtures optimieren

#### 1.3 Mock-Strategie entwickeln
- [ ] Mock-Strategie für externe Dienste definieren
- [ ] Mock-Factories erstellen
- [ ] Test-Daten-Generatoren implementieren

### Phase 2: Unit-Tests verbessern (Woche 3-4)

#### 2.1 Services-Tests
**Priorität: Hoch**
- [ ] `app/services/ai_service.py` (0% Coverage → Ziel: 80%)
- [ ] `app/services/user_service.py` (0% Coverage → Ziel: 80%)
- [ ] `app/services/knowledge_service.py` (0% Coverage → Ziel: 80%)
- [ ] `app/services/auth_service.py` (0% Coverage → Ziel: 80%)

#### 2.2 Core-Module Tests
**Priorität: Hoch**
- [ ] `app/core/security.py` (0% Coverage → Ziel: 90%)
- [ ] `app/core/database.py` (0% Coverage → Ziel: 90%)
- [ ] `app/core/config.py` (0% Coverage → Ziel: 90%)
- [ ] `app/core/session_manager.py` (0% Coverage → Ziel: 80%)

#### 2.3 Models-Tests
**Priorität: Mittel**
- [ ] `app/models/user.py` (0% Coverage → Ziel: 90%)
- [ ] `app/models/conversation.py` (0% Coverage → Ziel: 90%)
- [ ] `app/models/knowledge.py` (0% Coverage → Ziel: 90%)

### Phase 3: API-Endpoint Tests (Woche 5-6)

#### 3.1 Auth-Endpoints
**Priorität: Hoch**
- [ ] `app/api/v1/endpoints/auth.py` (24% Coverage → Ziel: 85%)
- [ ] `app/api/v1/endpoints/users.py` (0% Coverage → Ziel: 85%)

#### 3.2 Chat-Endpoints
**Priorität: Hoch**
- [ ] `app/api/v1/endpoints/chat.py` (37% Coverage → Ziel: 85%)
- [ ] `app/api/v1/endpoints/conversations.py` (41% Coverage → Ziel: 85%)

#### 3.3 Knowledge-Endpoints
**Priorität: Mittel**
- [ ] `app/api/v1/endpoints/document_endpoints.py` (58% Coverage → Ziel: 85%)
- [ ] `app/api/v1/endpoints/rag.py` (20% Coverage → Ziel: 80%)

### Phase 4: Integration-Tests (Woche 7-8)

#### 4.1 End-to-End Workflows
- [ ] Vollständiger Auth-Flow (Register → Login → Logout)
- [ ] Chat-Konversation Flow
- [ ] Dokument-Upload und -Verarbeitung
- [ ] Tool-Execution Flow

#### 4.2 Datenbank-Integration
- [ ] CRUD-Operationen Tests
- [ ] Transaktions-Tests
- [ ] Migration-Tests

### Phase 5: Performance & Security Tests (Woche 9-10)

#### 5.1 Performance-Tests
- [ ] API-Response-Zeit Tests
- [ ] Datenbank-Performance Tests
- [ ] Memory-Usage Tests
- [ ] Load-Tests

#### 5.2 Security-Tests
- [ ] Authentication Tests
- [ ] Authorization Tests
- [ ] Input-Validation Tests
- [ ] SQL-Injection Tests

## Technische Implementierung

### Mock-Strategie

```python
# Beispiel Mock-Implementierung
@pytest.fixture
def mock_weaviate_client():
    with patch('app.services.weaviate_service.weaviate_client') as mock:
        mock.search.return_value = {"results": []}
        yield mock

@pytest.fixture
def mock_redis_client():
    with patch('app.core.redis_client.redis_client') as mock:
        mock.get.return_value = None
        mock.set.return_value = True
        yield mock
```

### Test-Daten-Generatoren

```python
# Beispiel Test-Daten-Generator
class TestDataFactory:
    @staticmethod
    def create_user(**kwargs):
        return User(
            id=kwargs.get('id', uuid4()),
            email=kwargs.get('email', f"test{uuid4()}@example.com"),
            username=kwargs.get('username', f"testuser{uuid4()}"),
            **kwargs
        )
```

### Coverage-Ziele pro Modul

| Modul | Aktuelle Coverage | Ziel Coverage | Priorität |
|-------|------------------|---------------|-----------|
| ai_service.py | 0% | 80% | Hoch |
| user_service.py | 0% | 80% | Hoch |
| auth.py | 24% | 85% | Hoch |
| chat.py | 37% | 85% | Hoch |
| security.py | 0% | 90% | Hoch |
| database.py | 0% | 90% | Hoch |
| document_endpoints.py | 58% | 85% | Mittel |
| rag.py | 20% | 80% | Mittel |

## Qualitätsmetriken

### Coverage-Ziele
- **Gesamte Testabdeckung:** 44.3% → 80%
- **Kritische Module:** 90%+
- **API-Endpoints:** 85%+
- **Services:** 80%+

### Test-Qualität
- **Unit-Tests:** 60% der Gesamttests
- **Integration-Tests:** 30% der Gesamttests
- **E2E-Tests:** 10% der Gesamttests

### Performance-Ziele
- **Test-Ausführungszeit:** < 5 Minuten
- **Memory-Usage:** < 1GB
- **Test-Parallelisierung:** 4x Speedup

## Monitoring & Reporting

### Automatisierte Reports
- [ ] Tägliche Coverage-Reports
- [ ] Wöchentliche Trend-Analyse
- [ ] Coverage-Dashboard erstellen
- [ ] Slack/Teams Integration

### Quality Gates
- [ ] Coverage-Minimum: 80%
- [ ] Keine Regression in kritischen Modulen
- [ ] Alle Tests müssen durchlaufen
- [ ] Performance-Benchmarks einhalten

## Risiken & Mitigation

### Risiken
1. **Externe Dependencies:** Weaviate, Redis, etc.
2. **Test-Daten-Management:** Konsistente Test-Daten
3. **Performance:** Test-Ausführungszeit
4. **Maintenance:** Test-Pflege-Aufwand

### Mitigation-Strategien
1. **Comprehensive Mocking:** Alle externen Dienste mocken
2. **Test-Data-Factories:** Zentrale Test-Daten-Verwaltung
3. **Test-Parallelisierung:** CI/CD Optimierung
4. **Test-Dokumentation:** Klare Test-Struktur

## Erfolgsmetriken

### Kurzfristig (4 Wochen)
- [ ] Testabdeckung: 44.3% → 60%
- [ ] Fehlgeschlagene Tests: 263 → < 50
- [ ] Test-Ausführungszeit: < 10 Minuten

### Mittelfristig (8 Wochen)
- [ ] Testabdeckung: 60% → 75%
- [ ] Alle kritischen Module: > 80% Coverage
- [ ] Vollständige Integration-Tests

### Langfristig (12 Wochen)
- [ ] Testabdeckung: 75% → 80%
- [ ] Performance-Tests implementiert
- [ ] Security-Tests implementiert
- [ ] Automatisierte Quality Gates

## Nächste Schritte

### Sofort (Diese Woche)
1. [ ] Docker-Compose für Test-Umgebung erstellen
2. [ ] Pytest-Konfiguration korrigieren
3. [ ] Mock-Strategie implementieren
4. [ ] Erste Service-Tests schreiben

### Woche 1-2
1. [ ] Infrastruktur-Setup abschließen
2. [ ] Core-Module Tests implementieren
3. [ ] API-Endpoint Tests beginnen

### Woche 3-4
1. [ ] Services-Tests vervollständigen
2. [ ] Integration-Tests implementieren
3. [ ] Coverage-Monitoring einrichten

## Ressourcen & Tools

### Tools
- **Coverage:** pytest-cov
- **Mocking:** unittest.mock, pytest-mock
- **Test-Daten:** Faker, Factory Boy
- **Performance:** pytest-benchmark
- **Security:** Bandit, Safety

### Dokumentation
- [ ] Test-Writing Guidelines
- [ ] Mock-Strategie Dokumentation
- [ ] Test-Daten-Management Guide
- [ ] CI/CD Integration Guide

---

**Verantwortlich:** Entwicklungsteam  
**Review-Zyklus:** Wöchentlich  
**Nächste Review:** 3. August 2025