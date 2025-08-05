# DataExtract Microservice Integration Plan

## 📋 Übersicht

Dieser Plan beschreibt die Integration des **DataExtract** Projekts als Microservice in das bestehende **ConvoSphere** System. DataExtract bietet erweiterte Datei-Extraktionsfunktionen, die die bestehenden Dokumentenverarbeitungsfähigkeiten von ConvoSphere erheblich erweitern.

## 🎯 Ziele der Integration

### Primäre Ziele
1. **Erweiterte Dateiformat-Unterstützung**: Integration von 20+ zusätzlichen Dateiformaten
2. **Verbesserte Extraktionsqualität**: Nutzung von docling für erweiterte Datenextraktion
3. **Asynchrone Verarbeitung**: Skalierbare Batch-Verarbeitung großer Dateien
4. **Modulare Architektur**: Saubere Trennung der Extraktionslogik vom Hauptsystem
5. **Performance-Optimierung**: Parallele Verarbeitung und Caching

### Sekundäre Ziele
- **Monitoring & Observability**: Prometheus/Grafana Integration
- **Container-basierte Deployment**: Docker/Kubernetes Ready
- **API-Konsistenz**: Einheitliche Schnittstellen
- **Backward Compatibility**: Keine Breaking Changes

## 🏗️ Architektur-Design

### Aktuelle ConvoSphere Architektur
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Data Layer    │
                       │ (PostgreSQL,    │
                       │  Redis,         │
                       │  Weaviate)      │
                       └─────────────────┘
```

### Erweiterte Architektur mit DataExtract
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   DataExtract   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Microservice  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Data Layer    │    │   Processing    │
                       │ (PostgreSQL,    │    │   Queue         │
                       │  Redis,         │    │   (Redis/Celery)│
                       │  Weaviate)      │    └─────────────────┘
                       └─────────────────┘
```

## 🔧 Technische Integration

### 1. Service Discovery & Communication

#### Option A: HTTP API Integration (Empfohlen)
```python
# backend/app/services/dataextract_service.py
class DataExtractService:
    def __init__(self):
        self.base_url = "http://dataextract:8001"
        self.client = httpx.AsyncClient()
    
    async def extract_file(self, file_content: bytes, filename: str) -> dict:
        """Delegiert Extraktion an DataExtract Service"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/extract",
            files={"file": (filename, file_content)},
            data={
                "include_metadata": True,
                "include_text": True,
                "include_structure": True
            }
        )
        return response.json()
```

#### Option B: Message Queue Integration
```python
# Für asynchrone Verarbeitung großer Dateien
async def process_large_file(self, file_id: str):
    await self.celery_app.send_task(
        'dataextract.extract_file_async',
        args=[file_id],
        queue='dataextract'
    )
```

### 2. Datenmodell-Erweiterung

#### Neue Datenbank-Tabellen
```sql
-- Erweiterte Dokumenten-Metadaten
CREATE TABLE document_extraction_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    extraction_service VARCHAR(50) DEFAULT 'dataextract',
    extracted_text TEXT,
    structured_data JSONB,
    metadata JSONB,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Verarbeitungs-Jobs für DataExtract
CREATE TABLE dataextract_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    job_id VARCHAR(255),  -- DataExtract Job ID
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT
);
```

### 3. API-Integration

#### Neue Endpoints in ConvoSphere
```python
# backend/app/api/v1/endpoints/dataextract.py
@router.post("/documents/{document_id}/extract")
async def extract_document_with_dataextract(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Extrahiert Dokument mit DataExtract Service"""
    pass

@router.post("/documents/batch-extract")
async def batch_extract_documents(
    document_ids: List[str],
    current_user: User = Depends(get_current_user)
):
    """Batch-Extraktion mehrerer Dokumente"""
    pass

@router.get("/extraction/formats")
async def get_supported_formats():
    """Gibt unterstützte Dateiformate zurück"""
    pass
```

## 📦 Deployment-Strategie

### 1. Docker Compose Integration

#### Erweiterte docker-compose.yml
```yaml
services:
  # Bestehende Services...
  
  dataextract:
    build:
      context: ./services/dataextract
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - MAX_FILE_SIZE=157286400  # 150MB
      - WORKER_CONCURRENCY=4
      - ENABLE_OCR=true
      - ENABLE_MEDIA_EXTRACTION=true
    volumes:
      - ./services/dataextract/uploads:/app/uploads
      - ./services/dataextract/temp:/app/temp
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - convosphere-network
    restart: unless-stopped

  # Optional: Celery Worker für DataExtract
  dataextract-worker:
    build:
      context: ./services/dataextract
      dockerfile: Dockerfile
    command: celery -A app.workers.celery_app worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - dataextract
      - redis
    networks:
      - convosphere-network
    restart: unless-stopped
```

### 2. Kubernetes Deployment (Optional)
```yaml
# k8s/dataextract-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dataextract
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dataextract
  template:
    metadata:
      labels:
        app: dataextract
    spec:
      containers:
      - name: dataextract
        image: convosphere/dataextract:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
```

## 🔄 Migrationsplan

### Phase 1: Vorbereitung (1-2 Wochen)
1. **Code-Review & Anpassung**
   - DataExtract Code für ConvoSphere anpassen
   - API-Schnittstellen vereinheitlichen
   - Authentifizierung integrieren

2. **Datenbank-Migration**
   - Neue Tabellen erstellen
   - Indizes für Performance optimieren
   - Backup-Strategie definieren

3. **Testing-Infrastructure**
   - Unit Tests für Integration
   - Integration Tests
   - Performance Tests

### Phase 2: Staging Deployment (1 Woche)
1. **Staging Environment Setup**
   - DataExtract Service deployen
   - ConvoSphere Integration testen
   - Monitoring & Logging konfigurieren

2. **End-to-End Testing**
   - Datei-Upload Workflows
   - Extraktionsqualität validieren
   - Performance-Metriken sammeln

### Phase 3: Production Rollout (1 Woche)
1. **Gradual Rollout**
   - 10% Traffic auf DataExtract umleiten
   - Monitoring & Alerting aktivieren
   - Performance überwachen

2. **Full Migration**
   - 100% Traffic umstellen
   - Legacy-Extraktion deaktivieren
   - Cleanup durchführen

## 📊 Monitoring & Observability

### 1. Prometheus Metrics
```python
# DataExtract Service Metrics
dataextract_extraction_requests_total
dataextract_extraction_duration_seconds
dataextract_file_size_bytes
dataextract_supported_formats_total
dataextract_ocr_requests_total
dataextract_media_extraction_requests_total
```

### 2. Grafana Dashboards
- **Extraktions-Performance**: Durchsatz, Latenz, Erfolgsrate
- **Dateiformat-Verteilung**: Welche Formate werden am häufigsten verarbeitet
- **Resource Utilization**: CPU, Memory, Disk I/O
- **Error Rates**: Fehler nach Dateityp und Extraktionsmethode

### 3. Logging Strategy
```python
# Strukturiertes Logging
logger.info(
    "Document extraction completed",
    document_id=document_id,
    file_type=file_type,
    file_size=file_size,
    extraction_time=extraction_time,
    service="dataextract"
)
```

## 🔒 Security & Compliance

### 1. Authentication & Authorization
```python
# JWT Token Validation zwischen Services
async def validate_service_token(token: str) -> bool:
    """Validates JWT token for inter-service communication"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("service") == "convosphere"
    except JWTError:
        return False
```

### 2. Data Privacy
- **Temporary File Handling**: Automatische Bereinigung nach Verarbeitung
- **Encryption**: Dateien während Übertragung verschlüsseln
- **Audit Logging**: Vollständige Protokollierung aller Extraktionen

### 3. Rate Limiting
```python
# Service-spezifische Rate Limits
RATE_LIMITS = {
    "extract": "100/minute",
    "batch_extract": "10/minute",
    "large_files": "5/minute"
}
```

## 🧪 Testing Strategy

### 1. Unit Tests
```python
# tests/test_dataextract_integration.py
class TestDataExtractIntegration:
    async def test_extract_pdf_document(self):
        """Test PDF extraction through DataExtract service"""
        pass
    
    async def test_batch_extraction(self):
        """Test batch extraction of multiple documents"""
        pass
    
    async def test_large_file_handling(self):
        """Test handling of files > 50MB"""
        pass
```

### 2. Integration Tests
- **End-to-End Workflows**: Vollständige Dokumentenverarbeitung
- **Error Handling**: Netzwerk-Fehler, Service-Unavailable
- **Performance Tests**: Load Testing mit verschiedenen Dateigrößen

### 3. Contract Tests
```python
# API Contract Testing
def test_dataextract_api_contract():
    """Ensures DataExtract API matches expected schema"""
    pass
```

## 📈 Performance-Optimierung

### 1. Caching Strategy
```python
# Redis Caching für Extraktionsergebnisse
async def get_cached_extraction(file_hash: str) -> Optional[dict]:
    """Retrieve cached extraction result"""
    cached = await redis.get(f"extraction:{file_hash}")
    return json.loads(cached) if cached else None

async def cache_extraction_result(file_hash: str, result: dict):
    """Cache extraction result for 24 hours"""
    await redis.setex(
        f"extraction:{file_hash}",
        86400,  # 24 hours
        json.dumps(result)
    )
```

### 2. Parallel Processing
```python
# Concurrent file processing
async def process_multiple_files(files: List[UploadFile]):
    """Process multiple files concurrently"""
    tasks = [
        extract_file(file) for file in files
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 3. Resource Management
- **Memory Optimization**: Streaming für große Dateien
- **CPU Optimization**: Worker Pool Management
- **Disk I/O**: Temporary File Cleanup

## 🚀 Rollback Strategy

### 1. Feature Flags
```python
# Feature Flag für DataExtract Integration
USE_DATAEXTRACT = os.getenv("USE_DATAEXTRACT", "false").lower() == "true"

async def extract_document(file_content: bytes, filename: str):
    if USE_DATAEXTRACT:
        return await dataextract_service.extract_file(file_content, filename)
    else:
        return await legacy_extraction_service.extract_file(file_content, filename)
```

### 2. Gradual Rollback
1. **Traffic Reduction**: 100% → 50% → 0%
2. **Service Shutdown**: DataExtract Service stoppen
3. **Legacy Reactivation**: Bestehende Extraktion aktivieren

### 3. Data Recovery
- **Backup Restoration**: Datenbank-Backup wiederherstellen
- **File Recovery**: Nicht verarbeitete Dateien erneut verarbeiten

## 📋 Checkliste für Implementation

### Vor der Integration
- [ ] DataExtract Code Review abgeschlossen
- [ ] API-Schnittstellen definiert
- [ ] Datenbank-Schema erstellt
- [ ] Docker Images gebaut
- [ ] Monitoring konfiguriert

### Während der Integration
- [ ] Staging Environment deployed
- [ ] End-to-End Tests bestanden
- [ ] Performance Tests erfolgreich
- [ ] Security Review abgeschlossen
- [ ] Documentation aktualisiert

### Nach der Integration
- [ ] Production Deployment erfolgreich
- [ ] Monitoring aktiviert
- [ ] Team Training durchgeführt
- [ ] Support-Prozesse definiert
- [ ] Maintenance Schedule erstellt

## 🎯 Erfolgsmetriken

### Technische Metriken
- **Extraktionsqualität**: 95%+ Erfolgsrate
- **Performance**: < 30s für 50MB Dateien
- **Availability**: 99.9% Uptime
- **Error Rate**: < 1% Fehlerrate

### Business Metriken
- **User Adoption**: 80%+ Nutzung nach 1 Monat
- **File Format Support**: 20+ zusätzliche Formate
- **Processing Volume**: 10x höherer Durchsatz
- **User Satisfaction**: Verbesserte Extraktionsqualität

## 🔮 Zukünftige Erweiterungen

### Phase 2 Features
1. **AI-powered Extraction**: GPT-4 für bessere Texterkennung
2. **Multi-language Support**: Erweiterte Sprachunterstützung
3. **Custom Extractors**: Benutzerdefinierte Extraktoren
4. **Real-time Processing**: WebSocket-basierte Echtzeit-Verarbeitung

### Phase 3 Features
1. **Distributed Processing**: Kubernetes-basierte Skalierung
2. **Advanced Analytics**: ML-basierte Dokumentenanalyse
3. **Integration APIs**: Third-party Service Integration
4. **Mobile Support**: Native Mobile App Integration

---

**Autor**: AI Assistant  
**Datum**: $(date)  
**Version**: 1.0  
**Status**: Draft