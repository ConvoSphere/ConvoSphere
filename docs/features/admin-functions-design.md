# Phase 4: Admin-Funktionen – Backend-Design

## 1. Neue/erweiterte Datenmodelle

### a) User-Management
- User (Erweiterung):
  - id: UUID
  - username: str
  - email: str
  - role: Enum('user', 'premium', 'moderator', 'admin')
  - is_active: bool
  - created_at: datetime
  - last_login: datetime
  - profile: JSON (optional)

### b) Job-Monitoring
- BackgroundJob (neu):
  - id: UUID
  - job_type: Enum('import', 'embedding', 'processing', 'backup', 'restore', ...)
  - status: Enum('pending', 'running', 'completed', 'failed', 'cancelled')
  - progress: int (0-100)
  - user_id: UUID (optional)
  - document_id: UUID (optional)
  - started_at: datetime
  - finished_at: datetime
  - error_message: str (optional)
  - meta: JSON

### c) Backup-Management
- BackupJob (neu):
  - id: UUID
  - backup_type: Enum('database', 'documents', 'full')
  - status: Enum('pending', 'running', 'completed', 'failed')
  - created_at: datetime
  - finished_at: datetime
  - file_path: str
  - size: int
  - triggered_by: UUID
  - meta: JSON

### d) System-Monitoring
- SystemMetric (neu):
  - id: UUID
  - timestamp: datetime
  - cpu_usage: float
  - memory_usage: float
  - disk_usage: float
  - db_latency: float
  - api_response_time: float
  - error_rate: float
  - meta: JSON

---

## 2. API-Design (FastAPI)

### a) User-Management
- GET /api/v1/admin/users
- GET /api/v1/admin/users/{user_id}
- PUT /api/v1/admin/users/{user_id}
- DELETE /api/v1/admin/users/{user_id}
- POST /api/v1/admin/users/{user_id}/reset-password

### b) Job-Monitoring
- GET /api/v1/admin/jobs
- GET /api/v1/admin/jobs/{job_id}
- POST /api/v1/admin/jobs/{job_id}/cancel

### c) Backup-Management
- GET /api/v1/admin/backups
- POST /api/v1/admin/backups
- POST /api/v1/admin/backups/{backup_id}/restore
- DELETE /api/v1/admin/backups/{backup_id}

### d) System-Monitoring
- GET /api/v1/admin/system/metrics
- GET /api/v1/admin/system/health
- GET /api/v1/admin/system/logs

---

## 3. WebSocket-Events (Live-Updates)
- job_update: { job_id, status, progress, error_message }
- system_metric: { timestamp, cpu, memory, ... }

---

## 4. Berechtigungen
- Alle Endpunkte unter /api/v1/admin/* sind nur für Admins (und ggf. Moderatoren) zugänglich.
- JWT-Token muss Rolle prüfen (role in ['admin', 'moderator']).
- Aktionen wie Löschen, Restore, Rollenzuweisung: nur Admin.

---

## 5. Backend-Architektur/Services
- UserService: CRUD, Rollenverwaltung, Passwort-Reset
- JobService: Job-Tracking, Status-Updates, Abbruch
- BackupService: Backup/Restore, Dateiverwaltung, Automatisierung
- SystemMonitorService: Metrik-Sammlung, Health-Checks, Logging

---

## 6. Migrationen
- Alembic-Migrationen für neue Tabellen/Spalten:
  - background_jobs
  - backup_jobs
  - system_metrics
  - Erweiterung users (Rolle, Aktiv, Profil, etc.)

---

## 7. Tests
- Unit-Tests für alle neuen Services
- Integrationstests für Admin-APIs
- WebSocket-Tests für Live-Updates