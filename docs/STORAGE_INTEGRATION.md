# Storage Integration Documentation

## Übersicht

Die Knowledge Base wurde um eine flexible Cloud Storage Integration erweitert, die verschiedene Storage-Provider unterstützt:

- **Local Storage** (Standard für Entwicklung)
- **MinIO** (S3-kompatibel, Standard für Produktion)
- **AWS S3** (optional)
- **Google Cloud Storage** (optional)
- **Azure Blob Storage** (optional)

## Architektur

### Storage Provider Abstraktion

Die Implementierung verwendet eine abstrakte Storage-Architektur:

```
StorageManager
    ↓
StorageFactory
    ↓
StorageProvider (Interface)
    ↓
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ LocalStorage    │ MinIOStorage    │ S3Storage       │ GCSStorage      │
│ Provider        │ Provider        │ Provider        │ Provider        │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### Komponenten

1. **StorageProvider Interface** (`backend/app/services/storage/base.py`)
   - Definiert die Basis-Interface für alle Storage-Provider
   - Enthält Methoden für Upload, Download, Delete, etc.

2. **StorageConfig** (`backend/app/services/storage/config.py`)
   - Zentrale Konfiguration für alle Storage-Provider
   - Validierung der Provider-spezifischen Einstellungen

3. **StorageFactory** (`backend/app/services/storage/factory.py`)
   - Factory-Pattern für die Erstellung von Storage-Providern
   - Dynamische Registrierung neuer Provider

4. **StorageManager** (`backend/app/services/storage/manager.py`)
   - High-Level Interface für Storage-Operationen
   - Caching und Health-Check-Funktionalität

## Konfiguration

### Environment Variables

```bash
# Storage Configuration
STORAGE_PROVIDER=minio                    # local, minio, s3, gcs, azure
STORAGE_BUCKET_NAME=knowledge-base

# MinIO Configuration (default)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false

# S3 Configuration (alternative)
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY_ID=your_access_key
S3_SECRET_ACCESS_KEY=your_secret_key
S3_REGION=us-east-1

# GCS Configuration (alternative)
GCS_PROJECT_ID=your_project_id
GCS_CREDENTIALS_FILE=path/to/credentials.json

# Azure Configuration (alternative)
AZURE_ACCOUNT_NAME=your_account_name
AZURE_ACCOUNT_KEY=your_account_key
AZURE_CONNECTION_STRING=your_connection_string
```

### Docker Compose

MinIO ist standardmäßig in der Docker-Compose-Konfiguration enthalten:

```yaml
minio:
  image: minio/minio:latest
  container_name: convosphere_minio
  ports:
    - "9000:9000"      # API
    - "9001:9001"      # Web Console
  environment:
    - MINIO_ROOT_USER=${MINIO_ACCESS_KEY:-minioadmin}
    - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY:-minioadmin}
  command: server /data --console-address ":9001"
  volumes:
    - minio_data:/data
  networks:
    - convosphere-network
```

## Verwendung

### Knowledge Service Integration

Der `KnowledgeService` wurde erweitert, um Cloud Storage zu verwenden:

```python
# Dokument erstellen
document = await knowledge_service.create_document(
    user_id=user_id,
    title="Test Document",
    file_name="test.pdf",
    file_content=file_content,
    description="Test document description"
)

# Dokument verarbeiten
success = await knowledge_service.process_document(document.id)

# Dokument löschen
success = await knowledge_service.delete_document(document.id, user_id)
```

### Storage Manager

Direkte Verwendung des Storage Managers:

```python
from backend.app.services.storage.manager import StorageManager
from backend.app.services.storage.config import StorageConfig

# Konfiguration erstellen
config = StorageConfig(
    provider="minio",
    bucket_name="knowledge-base",
    minio_endpoint="localhost:9000",
    minio_access_key="minioadmin",
    minio_secret_key="minioadmin"
)

# Storage Manager erstellen
storage_manager = StorageManager(config)

# Dokument hochladen
storage_path = await storage_manager.upload_document(
    file_id="doc-123",
    content=file_content,
    metadata={"title": "Test Document"}
)

# Dokument herunterladen
content = await storage_manager.download_document(storage_path)

# Dokument löschen
success = await storage_manager.delete_document(storage_path)
```

## API Endpoints

### Storage Management

```http
# Storage Health Check
GET /api/v1/storage/health

# Storage Information
GET /api/v1/storage/info

# Available Providers
GET /api/v1/storage/providers

# Test Configuration
POST /api/v1/storage/test
{
  "provider": "minio",
  "bucket_name": "test-bucket",
  "minio_endpoint": "localhost:9000",
  "minio_access_key": "minioadmin",
  "minio_secret_key": "minioadmin"
}

# Get Configuration
GET /api/v1/storage/config

# Migrate Storage
POST /api/v1/storage/migrate
{
  "source_config": {...},
  "target_config": {...},
  "document_paths": ["path1", "path2"]
}

# Cleanup Orphaned Files
POST /api/v1/storage/cleanup
{
  "valid_storage_paths": ["path1", "path2"]
}
```

## Migration

### Von Local zu Cloud Storage

1. **Konfiguration ändern:**
   ```bash
   STORAGE_PROVIDER=minio
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   ```

2. **Dokumente migrieren:**
   ```python
   # Alle Dokument-Pfade aus der Datenbank abrufen
   documents = db.query(Document).all()
   storage_paths = [doc.file_path for doc in documents]
   
   # Migration durchführen
   results = await storage_manager.migrate_storage(
       source_config=local_config,
       target_config=minio_config,
       document_paths=storage_paths
   )
   ```

### Zwischen Cloud Providern

```python
# Von MinIO zu S3
source_config = StorageConfig(provider="minio", ...)
target_config = StorageConfig(provider="s3", ...)

results = await storage_manager.migrate_storage(
    source_config, target_config, document_paths
)
```

## Monitoring

### Health Checks

```python
# Storage Health Check
is_healthy = await storage_manager.health_check()

# Provider-spezifischer Health Check
is_healthy = await provider.health_check()
```

### Storage Information

```python
# Detaillierte Storage-Informationen
info = await storage_manager.get_storage_info()
# {
#   "provider": "minio",
#   "bucket_name": "knowledge-base",
#   "total_files": 150,
#   "total_size_bytes": 1048576,
#   "health_check_time": "2024-01-01T12:00:00Z"
# }
```

## Sicherheit

### Zugriffskontrolle

- **Benutzer-Isolation:** Dokumente sind benutzer-spezifisch
- **Bucket-Policies:** Cloud-Provider-spezifische Zugriffskontrolle
- **Presigned URLs:** Zeitlich begrenzter Zugriff auf Dokumente

### Verschlüsselung

- **Client-seitige Verschlüsselung:** Optional verfügbar
- **Server-seitige Verschlüsselung:** Cloud-Provider-spezifisch
- **Transport-Verschlüsselung:** HTTPS/TLS für alle Verbindungen

## Performance

### Optimierungen

1. **Chunked Uploads:** Große Dateien werden in Chunks hochgeladen
2. **Concurrent Uploads:** Mehrere Uploads parallel
3. **Caching:** Health-Check-Ergebnisse werden gecacht
4. **Connection Pooling:** Wiederverwendung von Verbindungen

### Monitoring

```python
# Performance-Metriken
metrics = {
    "upload_count": 0,
    "download_count": 0,
    "average_upload_time": 0.0,
    "average_download_time": 0.0,
    "error_count": 0
}
```

## Troubleshooting

### Häufige Probleme

1. **MinIO Connection Failed:**
   ```bash
   # MinIO Container Status prüfen
   docker ps | grep minio
   
   # MinIO Logs prüfen
   docker logs convosphere_minio
   ```

2. **Bucket Access Denied:**
   ```bash
   # Bucket-Policies prüfen
   # MinIO Console: http://localhost:9001
   ```

3. **Storage Path Issues:**
   ```python
   # Storage Path Format prüfen
   # Erwartetes Format: provider://bucket/path
   ```

### Debugging

```python
# Debug-Logging aktivieren
import logging
logging.getLogger("storage").setLevel(logging.DEBUG)

# Storage Manager Debug-Informationen
info = await storage_manager.get_storage_info()
print(f"Storage Info: {info}")
```

## Erweiterung

### Neuen Storage Provider hinzufügen

1. **Provider-Klasse erstellen:**
   ```python
   class CustomStorageProvider(StorageProvider):
       async def upload_file(self, file_path: str, content: bytes, metadata: dict = None) -> str:
           # Implementation
           pass
       
       async def download_file(self, storage_path: str) -> bytes:
           # Implementation
           pass
       
       # ... weitere Methoden
   ```

2. **Provider registrieren:**
   ```python
   StorageFactory.register_provider("custom", CustomStorageProvider)
   ```

3. **Konfiguration erweitern:**
   ```python
   class StorageConfig(BaseModel):
       # ... bestehende Felder
       custom_endpoint: str | None = None
       custom_credentials: str | None = None
   ```

## Tests

### Test Suite

```bash
# Storage Provider Tests
pytest tests/integration/backend/test_storage_providers.py -v

# Spezifische Provider Tests
pytest tests/integration/backend/test_storage_providers.py::TestStorageProviders::test_local_storage_provider -v
```

### Test Coverage

- ✅ Local Storage Provider
- ✅ MinIO Storage Provider
- ✅ Storage Factory
- ✅ Storage Manager
- ✅ Configuration Validation
- ✅ Error Handling
- ✅ Health Checks
- ✅ Migration Tests

## Deployment

### Production Setup

1. **MinIO Production:**
   ```yaml
   # docker-compose.prod.yml
   minio:
     image: minio/minio:latest
     environment:
       - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
       - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
     volumes:
       - minio_data:/data
     restart: unless-stopped
   ```

2. **S3 Production:**
   ```bash
   STORAGE_PROVIDER=s3
   S3_ACCESS_KEY_ID=your_production_key
   S3_SECRET_ACCESS_KEY=your_production_secret
   S3_REGION=us-east-1
   ```

3. **Backup Strategy:**
   ```bash
   # MinIO Backup
   docker run --rm -v minio_data:/data -v ./backup:/backup alpine tar czf /backup/minio_backup.tar.gz -C /data .
   ```

## Fazit

Die Storage Integration bietet eine **flexible, skalierbare und sichere** Lösung für die Knowledge Base:

- ✅ **Multi-Provider Support:** Local, MinIO, S3, GCS, Azure
- ✅ **Einfache Konfiguration:** Environment-basierte Konfiguration
- ✅ **Robuste Implementierung:** Fehlerbehandlung und Recovery
- ✅ **Monitoring:** Health Checks und Metriken
- ✅ **Migration:** Einfache Migration zwischen Providern
- ✅ **Sicherheit:** Zugriffskontrolle und Verschlüsselung
- ✅ **Performance:** Optimierte Upload/Download-Operationen

Die Implementierung ist **produktionsreif** und kann sofort verwendet werden.