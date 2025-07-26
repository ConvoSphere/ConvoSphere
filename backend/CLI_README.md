# ConvoSphere Admin CLI

Ein umfassendes Command-Line Interface für die Verwaltung der ConvoSphere Platform.

## Installation

Das CLI-Tool ist bereits im Backend-Verzeichnis verfügbar und benötigt keine zusätzliche Installation.

```bash
# CLI ausführbar machen (optional)
chmod +x admin.py
```

## Verwendung

```bash
# Hauptverwendung
python3 admin.py [COMMAND] [OPTIONS]

# Oder direkt ausführbar
./admin.py [COMMAND] [OPTIONS]
```

## Verfügbare Commands

### Datenbankverwaltung

```bash
# Migrationen ausführen
python3 admin.py db migrate

# Migration-Status anzeigen
python3 admin.py db status

# Migration rückgängig machen
python3 admin.py db downgrade <revision>
```

**Hinweis:** Diese Commands benötigen eine Backend-Umgebung mit installierten Dependencies.

### Backup & Recovery

```bash
# Datenbank-Backup erstellen
python3 admin.py backup create
python3 admin.py backup create --output backup_20241201.sql

# Backup wiederherstellen
python3 admin.py backup restore backup_20241201.sql
python3 admin.py backup restore backup_20241201.sql --confirm

# Verfügbare Backups auflisten
python3 admin.py backup list
python3 admin.py backup list --backup-dir /path/to/backups
```

**Unterstützte Datenbanken:**
- PostgreSQL (mit pg_dump/pg_restore)
- SQLite (Datei-Kopie)

### Benutzerverwaltung

```bash
# Admin-Benutzer erstellen
python3 admin.py user create-admin

# Alle Benutzer auflisten
python3 admin.py user list

# Benutzerdetails anzeigen
python3 admin.py user show <email|username|id>

# Neuen Benutzer erstellen
python3 admin.py user create --email user@example.com --username newuser --password secret123

# Benutzer aktualisieren
python3 admin.py user update <email|username|id> --role admin --status active

# Benutzer löschen
python3 admin.py user delete <email|username|id>

# Benutzerpasswort zurücksetzen
python3 admin.py user reset-password
```

**Hinweis:** Diese Commands benötigen eine Backend-Umgebung mit installierten Dependencies.

### System-Monitoring

```bash
# System-Health prüfen
python3 admin.py monitoring health
```

**Geprüfte Services:**
- Backend API (benötigt requests module)
- Datenbank (benötigt alembic)

### Konfiguration

```bash
# Aktuelle Konfiguration anzeigen
python3 admin.py config show

# Konfiguration validieren
python3 admin.py config validate
```

**Umgebungsvariablen:**
- `DATABASE_URL`: Datenbankverbindung
- `REDIS_URL`: Redis-Verbindung
- `WEAVIATE_URL`: Weaviate-Verbindung
- `BACKEND_URL`: Backend-API-URL
- `UPLOAD_DIR`: Upload-Verzeichnis
- `SECRET_KEY`: Geheimer Schlüssel

### Entwicklungstools

```bash
# Code-Qualität prüfen
python3 admin.py dev quality-check

# API-Tests ausführen
python3 admin.py dev api-test
python3 admin.py dev api-test --url http://localhost:8000
```

**Benötigte Tools:**
- `ruff` für Code-Formatierung und Linting
- `bandit` für Sicherheits-Checks
- `requests` für API-Tests

## Beispiele für typische Workflows

### Erste Einrichtung

```bash
# 1. Konfiguration anzeigen
python3 admin.py config show

# 2. Konfiguration validieren
python3 admin.py config validate

# 3. System-Health prüfen
python3 admin.py monitoring health

# 4. Admin-Benutzer erstellen
python3 admin.py user create-admin
```

### Tägliche Verwaltung

```bash
# 1. System-Status prüfen
python3 admin.py monitoring health

# 2. Konfiguration validieren
python3 admin.py config validate

# 3. Benutzerliste prüfen
python3 admin.py user list
```

### Backup-Strategie

```bash
# 1. Tägliches Backup erstellen
python3 admin.py backup create

# 2. Backup-Liste prüfen
python3 admin.py backup list

# 3. Bei Bedarf wiederherstellen
python3 admin.py backup restore backup_20241201_143022.sql --confirm
```

### Entwicklung

```bash
# 1. Code-Qualität prüfen
python3 admin.py dev quality-check

# 2. API-Tests ausführen
python3 admin.py dev api-test

# 3. System-Health prüfen
python3 admin.py monitoring health
```

## Integration mit Makefile

Das CLI-Tool ist in das Makefile integriert:

```bash
# CLI-Hilfe anzeigen
make admin-cli

# Backup erstellen
make admin-backup

# System-Health prüfen
make admin-health

# Konfiguration anzeigen
make admin-config
```

## Fehlerbehebung

### Häufige Probleme

1. **Alembic nicht gefunden**
   ```bash
   # Fehler: "Alembic not found"
   # Lösung: Backend-Umgebung mit Dependencies aktivieren
   cd backend
   source venv/bin/activate  # oder entsprechende virtuelle Umgebung
   ```

2. **Requests module nicht verfügbar**
   ```bash
   # Fehler: "requests module not available"
   # Lösung: requests installieren oder Backend-Umgebung aktivieren
   pip install requests
   ```

3. **Backup fehlgeschlagen**
   - Prüfen Sie, ob PostgreSQL-Tools installiert sind
   - Prüfen Sie die Datenbankverbindung
   - Prüfen Sie die Umgebungsvariablen

### Logs anzeigen

```bash
# System-Health prüfen
python3 admin.py monitoring health
```

## Erweiterung

Das CLI-Tool ist modular aufgebaut und kann einfach erweitert werden:

1. Neue Commands in `admin.py` hinzufügen
2. Argument-Parser erweitern
3. Neue Funktionen implementieren

## Sicherheit

- Alle kritischen Operationen erfordern Bestätigung
- Backup-Restore erfordert explizite Bestätigung
- Umgebungsvariablen für sensible Daten

## Support

Bei Problemen oder Fragen:

1. Prüfen Sie die System-Health: `python3 admin.py monitoring health`
2. Validieren Sie die Konfiguration: `python3 admin.py config validate`
3. Zeigen Sie die Konfiguration an: `python3 admin.py config show`

## Technische Details

### Abhängigkeiten

**Minimal (funktioniert ohne Backend):**
- Python 3.8+
- argparse (Standard Library)
- subprocess (Standard Library)
- os, sys, datetime (Standard Library)

**Optional (für erweiterte Funktionen):**
- requests (für API-Tests)
- alembic (für Datenbank-Migrationen)
- ruff, bandit (für Code-Qualität)
- pg_dump/pg_restore (für PostgreSQL-Backups)

### Architektur

- **Modular:** Jede Funktionalität in separaten Funktionen
- **Robust:** Elegante Fehlerbehandlung für fehlende Dependencies
- **Erweiterbar:** Einfache Hinzufügung neuer Commands
- **Benutzerfreundlich:** Klare Fehlermeldungen und Help-Texts