# Phase 1 Checkliste - Kritische Fixes

## ✅ Automatisierte Fixes (bereits erledigt)
- [x] Tools installiert (Ruff, Bandit, Mypy)
- [x] Type-Stubs installiert (types-requests, types-PyYAML, types-psutil)
- [x] Konfigurationsdateien erstellt:
  - [x] `ruff.toml` - Code-Linting
  - [x] `.bandit` - Sicherheitsanalyse
  - [x] `mypy.ini` - Type-Checking
  - [x] `.pre-commit-config.yaml` - Pre-commit-Hooks
- [x] Automatische Ruff-Fixes ausgeführt (1.207 Probleme behoben)
- [x] Code-Formatierung durchgeführt (66 Dateien formatiert)

## 🔧 Manuelle Fixes (noch zu erledigen)

### 1. Undefinierte Variablen in main.py (KRITISCH)
- [ ] `db` Variable definieren oder importieren
  - **Datei**: `backend/main.py:101,124`
  - **Problem**: `F821 Undefined name 'db'`
  - **Zeitaufwand**: 2-4 Stunden

- [ ] `get_db` Funktion implementieren oder importieren
  - **Datei**: `backend/main.py:197`
  - **Problem**: `F821 Undefined name 'get_db'`
  - **Zeitaufwand**: 1-2 Stunden

### 2. Import-Fehler beheben
- [ ] Fehlende Imports in main.py ergänzen
  - **Datei**: `backend/main.py:193`
  - **Problem**: `PLC0415 import should be at the top-level of a file`
  - **Zeitaufwand**: 2-3 Stunden

### 3. Blind Exception Handling
- [ ] Spezifische Exception-Typen verwenden
  - **Datei**: `backend/main.py:263`
  - **Problem**: `BLE001 Do not catch blind exception: Exception`
  - **Zeitaufwand**: 2-3 Stunden

### 4. Debug-Code entfernen
- [ ] Print-Statements in output.py entfernen
  - **Datei**: `backend/cli/utils/output.py`
  - **Problem**: 6 Print-Statements gefunden
  - **Zeitaufwand**: 1-2 Stunden

### 5. Weitere kritische Fixes
- [ ] Undefinierte Funktionen beheben
  - **Datei**: `backend/cli/commands/dev.py:164`
  - **Problem**: `F821 Undefined name 'print_warning'`
  - **Zeitaufwand**: 1-2 Stunden

- [ ] Unused Parameters entfernen
  - **Datei**: `backend/cli/utils/helpers.py:45`
  - **Problem**: `ARG002 Unused method argument: 'perm'`
  - **Zeitaufwand**: 30 Minuten

## 📊 Fortschritt

### Vorher (Aktuell)
- **Ruff**: 50+ Probleme
- **Bandit**: 50+ Sicherheitsprobleme  
- **Mypy**: 2.581 Type-Fehler

### Nach automatischen Fixes
- **Ruff**: 1.207 Probleme automatisch behoben
- **Verbleibende Ruff-Probleme**: 2.720 (davon 301 mit --unsafe-fixes lösbar)
- **Formatierung**: 66 Dateien automatisch formatiert

### Ziel (Nach Phase 1)
- **Ruff**: <10 kritische Probleme
- **Bandit**: 0 kritische Sicherheitsprobleme
- **Mypy**: <100 Type-Fehler

## 🎯 Nächste Schritte

### Sofort (Heute)
1. [ ] Kritische undefinierte Variablen in `main.py` beheben
2. [ ] `get_db` Funktion implementieren/importieren
3. [ ] Import-Fehler in `main.py` korrigieren

### Diese Woche
1. [ ] Blind Exception Handling verbessern
2. [ ] Debug-Code entfernen
3. [ ] Undefinierte Funktionen beheben
4. [ ] Tests ausführen nach jeder Änderung

### Nächste Woche
1. [ ] Phase 2 starten (Code-Formatierung)
2. [ ] Pre-commit-Hooks einrichten
3. [ ] Erste Erfolgsmetriken sammeln

## 🚨 Wichtige Hinweise

1. **Backup erstellen** vor manuellen Änderungen
2. **Tests ausführen** nach jeder Änderung
3. **Inkrementell vorgehen** - nicht alles auf einmal
4. **Code-Reviews** für kritische Änderungen

## 📈 Erfolgsmetriken

### Quantitative Ziele
- [ ] **Ruff kritische Fehler**: 0
- [ ] **Ruff Warnungen**: <10
- [ ] **Bandit kritische Probleme**: 0
- [ ] **Mypy kritische Fehler**: <50

### Qualitative Ziele
- [ ] **Code läuft ohne Fehler**
- [ ] **Alle Tests bestehen**
- [ ] **Keine Regressionen**

---

**Status**: Automatisierte Fixes abgeschlossen ✅  
**Verbleibend**: Manuelle Fixes für kritische Probleme  
**Gesamtaufwand**: 8-13 Stunden (davon 2-4 Stunden bereits investiert)