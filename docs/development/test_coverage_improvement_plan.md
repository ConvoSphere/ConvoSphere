# Plan zur Erhöhung der Testabdeckung

## Aktuelle Situation
- **Gesamtabdeckung**: 30%
- **Erfolgreiche Tests**: 7/7 Konfigurationstests
- **Hauptprobleme**: Import-Fehler, fehlende Datenbankverbindung, niedrige Abdeckung bei kritischen Modulen

## Phase 1: Infrastruktur-Fixes (Priorität: Hoch)

### 1.1 Import-Probleme beheben
**Ziel**: Alle Tests lauffähig machen
**Zeitaufwand**: 1-2 Tage

#### Aufgaben:
- [ ] Alle verbleibenden Import-Fehler in Test-Dateien korrigieren
- [ ] `conftest.py` vollständig reparieren
- [ ] Test-Fixtures und Mock-Objekte korrekt konfigurieren
- [ ] Blackbox-Tests importieren lassen
- [ ] Integration-Tests importieren lassen
- [ ] Performance-Tests importieren lassen

#### Betroffene Dateien:
```
tests/blackbox/backend/
tests/integration/backend/
tests/performance/backend/
tests/conftest.py
```

### 1.2 Test-Datenbank einrichten
**Ziel**: Schnelle und einfache Tests ermöglichen
**Zeitaufwand**: 1 Tag

#### Aufgaben:
- [ ] SQLite für Unit-Tests konfigurieren (Sofort)
- [ ] Cross-database UUID-Support implementieren
- [ ] Test-Fixtures für SQLite-Daten erstellen
- [ ] Datenbank-Cleanup nach Tests implementieren
- [ ] Optional: PostgreSQL für Integration-Tests (Docker-Compose)

### 1.3 Mock-Infrastruktur verbessern
**Ziel**: Externe Dienste zuverlässig mocken
**Zeitaufwand**: 2-3 Tage

#### Aufgaben:
- [ ] AI-Service Mocks (OpenAI, Anthropic, etc.)
- [ ] Weaviate-Service Mocks
- [ ] Redis-Service Mocks
- [ ] OAuth-Service Mocks
- [ ] SAML-Service Mocks
- [ ] File-Upload Mocks
- [ ] WebSocket Mocks

## Phase 2: Kritische Services testen (Priorität: Hoch)

### 2.1 Authentication & Authorization (0-30% Abdeckung)
**Ziel**: 80%+ Abdeckung
**Zeitaufwand**: 3-4 Tage

#### Zu testende Module:
```
backend/app/services/auth_service.py
backend/app/services/saml_service.py
backend/app/services/oauth_service.py
backend/app/api/v1/endpoints/auth.py
backend/app/api/v1/endpoints/sso.py
backend/app/api/v1/endpoints/rbac_management.py
```

#### Test-Strategie:
- [ ] Unit-Tests für alle Auth-Funktionen
- [ ] Integration-Tests für Login/Logout-Flows
- [ ] Security-Tests für Token-Validierung
- [ ] RBAC-Tests für Rollen und Berechtigungen
- [ ] SAML/OAuth-Integration-Tests

### 2.2 Core Business Services (10-30% Abdeckung)
**Ziel**: 70%+ Abdeckung
**Zeitaufwand**: 5-7 Tage

#### Priorität 1 - Kritische Services:
```
backend/app/services/user_service.py (23KB)
backend/app/services/conversation_service.py (11KB)
backend/app/services/assistant_service.py (12KB)
backend/app/services/knowledge_service.py (30KB)
```

#### Priorität 2 - Wichtige Services:
```
backend/app/services/rag_service.py (28KB)
backend/app/services/ai_service.py (36KB)
backend/app/services/embedding_service.py (31KB)
backend/app/services/conversation_intelligence_service.py (35KB)
```

#### Test-Strategie:
- [ ] Unit-Tests für alle Service-Methoden
- [ ] Mock externe Dependencies
- [ ] Test Edge Cases und Error-Handling
- [ ] Test Performance-Critical Paths
- [ ] Test Business Logic Validierung

## Phase 3: API-Endpunkte testen (Priorität: Mittel)

### 3.1 Kritische Endpunkte (20-40% Abdeckung)
**Ziel**: 70%+ Abdeckung
**Zeitaufwand**: 4-6 Tage

#### Priorität 1 - User-Facing APIs:
```
backend/app/api/v1/endpoints/chat.py (17KB)
backend/app/api/v1/endpoints/conversations.py (6.5KB)
backend/app/api/v1/endpoints/users.py (19KB)
backend/app/api/v1/endpoints/assistants_management.py (9.5KB)
```

#### Priorität 2 - Admin APIs:
```
backend/app/api/v1/endpoints/domain_groups.py (25KB)
backend/app/api/v1/endpoints/conversation_intelligence.py (14KB)
backend/app/api/v1/endpoints/hybrid_mode.py (15KB)
```

#### Test-Strategie:
- [ ] HTTP-Status-Code Tests
- [ ] Request/Response Schema Tests
- [ ] Authentication/Authorization Tests
- [ ] Error-Handling Tests
- [ ] Rate-Limiting Tests
- [ ] Input-Validation Tests

### 3.2 WebSocket-Endpunkte (0% Abdeckung)
**Ziel**: 60%+ Abdeckung
**Zeitaufwand**: 2-3 Tage

```
backend/app/api/v1/endpoints/websocket.py (26KB)
```

#### Test-Strategie:
- [ ] WebSocket-Verbindung Tests
- [ ] Message-Handling Tests
- [ ] Connection-Lifecycle Tests
- [ ] Error-Handling Tests

## Phase 4: Tools und Utilities testen (Priorität: Mittel)

### 4.1 Tool-Services (0-60% Abdeckung)
**Ziel**: 70%+ Abdeckung
**Zeitaufwand**: 3-4 Tage

```
backend/app/services/tool_service.py (14KB)
backend/app/services/tool_executor.py (17KB)
backend/app/services/tool_executor_v2.py (20KB)
backend/app/api/v1/endpoints/tools.py (11KB)
```

#### Test-Strategie:
- [ ] Tool-Registration Tests
- [ ] Tool-Execution Tests
- [ ] Error-Handling Tests
- [ ] Security Tests für Tool-Execution

### 4.2 Utility-Funktionen
**Ziel**: 80%+ Abdeckung
**Zeitaufwand**: 2-3 Tage

```
backend/app/utils/
backend/app/core/
```

## Phase 5: Integration und E2E Tests (Priorität: Niedrig)

### 5.1 Workflow-Integration-Tests
**Ziel**: Vollständige User-Journeys testen
**Zeitaufwand**: 4-6 Tage

#### Test-Szenarien:
- [ ] User-Registration → Login → Chat → Logout
- [ ] Document-Upload → Processing → Search
- [ ] Assistant-Creation → Training → Usage
- [ ] Knowledge-Base-Erstellung → RAG-Integration
- [ ] Multi-Agent-Konversationen

### 5.2 Performance-Tests
**Ziel**: Performance-Benchmarks etablieren
**Zeitaufwand**: 3-4 Tage

```
tests/performance/backend/
```

#### Test-Szenarien:
- [ ] Load-Tests für Chat-API
- [ ] Database-Performance-Tests
- [ ] AI-Service-Response-Time Tests
- [ ] Memory-Usage Tests
- [ ] Concurrent-User Tests

## Phase 6: Security und Quality Assurance (Priorität: Hoch)

### 6.1 Security-Tests
**Ziel**: Sicherheitslücken identifizieren
**Zeitaufwand**: 3-4 Tage

```
tests/security/backend/
```

#### Test-Bereiche:
- [ ] SQL-Injection Tests
- [ ] XSS-Tests
- [ ] CSRF-Tests
- [ ] Authentication-Bypass Tests
- [ ] Authorization-Tests
- [ ] Input-Validation Tests
- [ ] Rate-Limiting Tests

### 6.2 Code-Quality-Tests
**Ziel**: Code-Qualität sicherstellen
**Zeitaufwand**: 1-2 Tage

#### Tools:
- [ ] Pylint/Flake8 Integration
- [ ] Type-Checking mit mypy
- [ ] Security-Scanning mit bandit
- [ ] Dependency-Vulnerability-Scanning

## Implementierungsplan

### Woche 1: Infrastruktur
- Tag 1-2: Import-Probleme beheben
- Tag 3: Test-Datenbank einrichten
- Tag 4-5: Mock-Infrastruktur verbessern

### Woche 2-3: Kritische Services
- Tag 1-4: Auth-Services testen
- Tag 5-7: Core Business Services (Priorität 1)
- Tag 8-10: Core Business Services (Priorität 2)

### Woche 4-5: API-Endpunkte
- Tag 1-4: Kritische Endpunkte testen
- Tag 5-7: WebSocket-Endpunkte testen

### Woche 6: Tools und Utilities
- Tag 1-3: Tool-Services testen
- Tag 4-5: Utility-Funktionen testen

### Woche 7-8: Integration und Security
- Tag 1-4: Integration-Tests
- Tag 5-7: Security-Tests

## Erfolgsmetriken

### Kurzfristige Ziele (4 Wochen):
- [ ] Gesamtabdeckung: 60%+
- [ ] Kritische Services: 80%+
- [ ] Auth-Services: 90%+
- [ ] Alle Tests lauffähig

### Mittelfristige Ziele (8 Wochen):
- [ ] Gesamtabdeckung: 80%+
- [ ] Alle Services: 70%+
- [ ] API-Endpunkte: 80%+
- [ ] Security-Tests: 100%

### Langfristige Ziele (12 Wochen):
- [ ] Gesamtabdeckung: 85%+
- [ ] Performance-Tests implementiert
- [ ] E2E-Tests implementiert
- [ ] CI/CD-Pipeline integriert

## Tools und Technologien

### Test-Framework:
- pytest (bereits konfiguriert)
- pytest-asyncio (für async Tests)
- pytest-cov (für Coverage)

### Mocking:
- unittest.mock
- pytest-mock
- responses (für HTTP-Mocks)

### Test-Datenbank:
- **SQLite** (Hauptsächlich für Unit-Tests)
- **PostgreSQL** (Optional für Integration-Tests)
- Factory Boy (für Test-Daten)
- pytest-sqlite (für SQLite-spezifische Tests)

### Security-Testing:
- bandit (Security-Scanner)
- safety (Dependency-Scanner)

### Performance-Testing:
- locust (Load-Testing)
- pytest-benchmark

## Risiken und Mitigation

### Risiko 1: Komplexe Dependencies
**Mitigation**: Schrittweise Mock-Implementierung, Priorisierung nach Wichtigkeit

### Risiko 2: Performance-Impact
**Mitigation**: Separate Test-Umgebung, Optimierte Test-Fixtures

### Risiko 3: Flaky Tests
**Mitigation**: Robuste Test-Fixtures, Proper Cleanup, Deterministic Tests

### Risiko 4: Zeitaufwand
**Mitigation**: Priorisierung nach Business-Impact, Iterative Implementierung

## Nächste Schritte

1. **Sofort**: Import-Probleme beheben
2. **Diese Woche**: Test-Datenbank einrichten
3. **Nächste Woche**: Auth-Services testen
4. **Folgende Woche**: Core Business Services testen

## Monitoring und Reporting

### Wöchentliche Reports:
- Test-Abdeckung pro Modul
- Anzahl fehlgeschlagener Tests
- Performance-Metriken
- Security-Issues

### Tools:
- Coverage-Reports (HTML + Terminal)
- Test-Execution-Reports
- Performance-Benchmarks
- Security-Scan-Reports