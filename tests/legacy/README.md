# Legacy Tests

## 📋 **Übersicht**

Dieses Verzeichnis enthält **Legacy-Tests** für die alte monolithische AI-Service Implementierung. Diese Tests wurden während der Refaktorierung zu einer modularen Architektur erstellt und sind **nicht mehr aktiv**.

## 📁 **Dateien**

- `test_ai_service_legacy.py` - Tests für die alte monolithische AI-Service Implementierung (731 Zeilen)

## ⚠️ **Wichtiger Hinweis**

### **Diese Tests sind DEPRECATED!**

- ❌ **Nicht mehr aktiv** - werden nicht mehr ausgeführt
- ❌ **Testen alte Implementierung** - nicht die aktuelle modulare Architektur
- ❌ **Können fehlschlagen** - weil sie die alte API erwarten

### **Aktuelle Tests**

Die aktuellen, aktiven Tests befinden sich in:
- `tests/unit/backend/services/test_ai_service.py` - Tests für aktuelle modulare Implementierung
- `tests/unit/backend/services/test_ai_core.py` - Tests für Core-Komponenten
- `tests/unit/backend/services/test_ai_middleware.py` - Tests für Middleware-Komponenten
- `tests/unit/backend/services/test_ai_types.py` - Tests für Type-Definitionen
- `tests/unit/backend/services/test_ai_service_refactored.py` - Tests für refaktorierten Service
- `tests/integration/services/test_ai_middleware_pipeline.py` - Integration-Tests

## 🔄 **Migration**

### **Warum sind diese Tests hier?**

Diese Tests werden **nur für Referenzzwecke** aufbewahrt:

1. **Historische Dokumentation** - zeigen, wie die alte Implementierung funktionierte
2. **Migration-Hilfe** - können bei der Migration von Legacy-Code helfen
3. **Fallback-Option** - falls Probleme mit der neuen Implementierung auftreten

### **Wann können diese Tests entfernt werden?**

Diese Tests können entfernt werden, wenn:

1. ✅ **Neue Tests vollständig** - alle Funktionalitäten in neuen Tests abgedeckt
2. ✅ **Migration abgeschlossen** - alle Legacy-Integrationen migriert
3. ✅ **Stabilität bestätigt** - neue Implementierung ist stabil und getestet
4. ✅ **Team-Einverständnis** - alle Entwickler sind mit der neuen Architektur vertraut

## 🧪 **Test-Ausführung**

### **Legacy-Tests ausführen (nicht empfohlen):**
```bash
# Nur für Debugging-Zwecke
pytest tests/legacy/test_ai_service_legacy.py -v
```

### **Aktuelle Tests ausführen (empfohlen):**
```bash
# Alle aktuellen AI-Service Tests
pytest tests/unit/backend/services/test_ai_service.py -v
pytest tests/unit/backend/services/test_ai_core.py -v
pytest tests/unit/backend/services/test_ai_middleware.py -v
pytest tests/unit/backend/services/test_ai_types.py -v
pytest tests/unit/backend/services/test_ai_service_refactored.py -v
pytest tests/integration/services/test_ai_middleware_pipeline.py -v
```

## 📊 **Test-Statistiken**

### **Legacy-Tests (DEPRECATED):**
- **Dateien**: 1
- **Zeilen**: 731
- **Status**: Nicht mehr aktiv

### **Aktuelle Tests:**
- **Dateien**: 6
- **Zeilen**: 2.384
- **Status**: Aktiv und empfohlen
- **Coverage**: 95%+

## 🚀 **Nächste Schritte**

1. **Neue Tests verwenden** - nur die aktuellen Tests für Entwicklung
2. **Legacy-Tests ignorieren** - nicht mehr ausführen oder warten
3. **Migration abschließen** - alle Legacy-Integrationen auf neue Architektur umstellen
4. **Legacy-Tests entfernen** - nach vollständiger Migration

---

**Hinweis**: Diese Legacy-Tests sind Teil der Refaktorierung von Phase 6 und werden nach Abschluss der Migration entfernt.