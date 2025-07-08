# ConvoSphere CLI Management Tool

Das ConvoSphere CLI-Tool bietet umfassende Verwaltungsfunktionen für die ConvoSphere-Plattform.

## Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements-cli.txt

# CLI-Tool ausführbar machen
chmod +x scripts/convosphere.py
```

## Verwendung

### Grundlegende Syntax

```bash
python scripts/convosphere.py [COMMAND] [OPTIONS]
```

### User Management

```bash
# Alle Benutzer auflisten
python scripts/convosphere.py users list

# Neuen Benutzer erstellen
python scripts/convosphere.py users create --email admin@example.com --password secret123 --role admin

# Benutzer aktualisieren
python scripts/convosphere.py users update --user-id 123 --role moderator

# Benutzer löschen
python scripts/convosphere.py users delete --user-id 123

# Passwort zurücksetzen
python scripts/convosphere.py users reset-password --user-id 123 --password newpassword
```

### Database Management

```bash
# Datenbankstatus prüfen
python scripts/convosphere.py database status

# Migrationen ausführen
python scripts/convosphere.py database migrate

# Backup erstellen
python scripts/convosphere.py database backup --file backup_2024.sql

# Backup wiederherstellen
python scripts/convosphere.py database restore --file backup_2024.sql

# Datenbank zurücksetzen (ACHTUNG: Löscht alle Daten!)
python scripts/convosphere.py database reset --force
```

### Service Management

```bash
# Service-Status anzeigen
python scripts/convosphere.py services status

# Services starten
python scripts/convosphere.py services start

# Spezifischen Service starten
python scripts/convosphere.py services start --service backend

# Services stoppen
python scripts/convosphere.py services stop

# Services neustarten
python scripts/convosphere.py services restart

# Logs anzeigen
python scripts/convosphere.py services logs --service backend --tail 100
```

### Deployment

```bash
# Deployment in Entwicklungsumgebung
python scripts/convosphere.py deploy dev

# Deployment in Produktionsumgebung
python scripts/convosphere.py deploy prod --force

# Deployment ohne Build
python scripts/convosphere.py deploy staging --build false
```

### System Health

```bash
# System-Gesundheit prüfen
python scripts/convosphere.py health

# Detaillierte Gesundheitsinformationen
python scripts/convosphere.py health --detailed
```

### Configuration Management

```bash
# Aktuelle Konfiguration anzeigen
python scripts/convosphere.py config show

# Konfigurationswert setzen
python scripts/convosphere.py config set --key DB_HOST --value localhost

# Konfigurationswert abrufen
python scripts/convosphere.py config get --key DB_HOST

# Konfiguration zurücksetzen
python scripts/convosphere.py config reset
```

### Logs

```bash
# Alle Logs anzeigen
python scripts/convosphere.py logs

# Spezifische Service-Logs
python scripts/convosphere.py logs --service backend

# Logs mit Follow-Modus
python scripts/convosphere.py logs --service frontend --follow

# Bestimmte Anzahl Zeilen
python scripts/convosphere.py logs --tail 50
```

## Konfiguration

Das CLI-Tool verwendet die Konfigurationsdatei `config/cli.yaml`:

```yaml
# Database settings
database:
  host: localhost
  port: 5432
  name: convosphere
  user: postgres
  password: password

# Docker settings
docker:
  compose_file: docker-compose.yml
  project_name: convosphere
```

## Umgebungsvariablen

Das Tool liest auch Umgebungsvariablen aus der `.env`-Datei:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=convosphere
DB_USER=postgres
DB_PASSWORD=password
```

## Sicherheit

- Alle sensiblen Operationen erfordern Bestätigung
- Passwörter werden gehashed gespeichert
- Backup-Dateien werden sicher verwaltet
- Logs enthalten keine sensiblen Daten

## Troubleshooting

### Häufige Probleme

1. **Datenbankverbindung fehlgeschlagen**
   - Prüfen Sie die Datenbankeinstellungen in `.env`
   - Stellen Sie sicher, dass PostgreSQL läuft

2. **Docker nicht gefunden**
   - Installieren Sie Docker und Docker Compose
   - Stellen Sie sicher, dass Docker läuft

3. **Berechtigungsfehler**
   - Stellen Sie sicher, dass Sie die notwendigen Rechte haben
   - Verwenden Sie `sudo` bei Bedarf

### Debug-Modus

```bash
# Debug-Informationen aktivieren
export CONVOSPHERE_DEBUG=1
python scripts/convosphere.py [COMMAND]
```

## Erweiterte Funktionen

### Automatisierung

```bash
# Backup-Skript für Cron
#!/bin/bash
python scripts/convosphere.py database backup --file /backups/auto_$(date +%Y%m%d_%H%M%S).sql
```

### Monitoring

```bash
# Health-Check-Skript
#!/bin/bash
if ! python scripts/convosphere.py health --detailed; then
    echo "System unhealthy, sending alert..."
    # Alert-Logik hier
fi
```

## Support

Bei Problemen oder Fragen:

1. Prüfen Sie die Logs: `python scripts/convosphere.py logs`
2. Führen Sie einen Health-Check aus: `python scripts/convosphere.py health --detailed`
3. Konsultieren Sie die Dokumentation
4. Erstellen Sie ein Issue im Repository 