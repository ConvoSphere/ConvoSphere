# DataExtract Implementation Roadmap

## 🗓️ Timeline: 4-6 Wochen

### Woche 1-2: Foundation & Setup

#### Tag 1-3: Repository Setup & Code Review
```bash
# 1. DataExtract Repository klonen und analysieren
git clone https://github.com/ConvoSphere/DataExtract.git services/dataextract
cd services/dataextract

# 2. Code Review durchführen
# - API-Schnittstellen verstehen
# - Abhängigkeiten identifizieren
# - Konfigurationsoptionen dokumentieren
```

#### Tag 4-5: Docker Setup
```dockerfile
# services/dataextract/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# UV installieren
RUN pip install uv

# Dependencies installieren
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Application Code kopieren
COPY . .

# Port exponieren
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Tag 6-7: Docker Compose Integration
```yaml
# docker-compose.yml erweitern
services:
  dataextract:
    build:
      context: ./services/dataextract
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - MAX_FILE_SIZE=157286400
      - WORKER_CONCURRENCY=4
    volumes:
      - ./services/dataextract/uploads:/app/uploads
      - ./services/dataextract/temp:/app/temp
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - convosphere-network
```

### Woche 2-3: Backend Integration

#### Tag 8-10: Service Layer Implementation
```python
# backend/app/services/dataextract_service.py
import httpx
import logging
from typing import Optional, Dict, Any
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

class DataExtractService:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.dataextract_url or "http://dataextract:8000"
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 min timeout
    
    async def extract_file(
        self, 
        file_content: bytes, 
        filename: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extrahiert Datei mit DataExtract Service"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/extract",
                files={"file": (filename, file_content)},
                data={
                    "include_metadata": True,
                    "include_text": True,
                    "include_structure": True,
                    **(options or {})
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"DataExtract API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in DataExtract service: {e}")
            raise
    
    async def extract_file_async(
        self, 
        file_content: bytes, 
        filename: str,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Startet asynchrone Extraktion"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/extract/async",
                files={"file": (filename, file_content)},
                data={
                    "include_metadata": True,
                    "include_text": True,
                    "include_structure": True,
                    **(options or {})
                }
            )
            response.raise_for_status()
            return response.json()["job_id"]
        except httpx.HTTPError as e:
            logger.error(f"DataExtract async API error: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Abfragt Status eines asynchronen Jobs"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/jobs/{job_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"DataExtract job status error: {e}")
            raise
    
    async def get_supported_formats(self) -> Dict[str, Any]:
        """Gibt unterstützte Dateiformate zurück"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/formats")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"DataExtract formats error: {e}")
            raise
    
    async def close(self):
        """Schließt HTTP Client"""
        await self.client.aclose()
```

#### Tag 11-12: Database Migration
```sql
-- migrations/versions/xxx_add_dataextract_tables.sql
-- Erweiterte Dokumenten-Metadaten
CREATE TABLE document_extraction_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    extraction_service VARCHAR(50) DEFAULT 'dataextract',
    extracted_text TEXT,
    structured_data JSONB,
    metadata JSONB,
    processing_time_ms INTEGER,
    file_hash VARCHAR(64),  -- Für Caching
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
    options JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Indizes für Performance
CREATE INDEX idx_document_extraction_results_document_id ON document_extraction_results(document_id);
CREATE INDEX idx_document_extraction_results_file_hash ON document_extraction_results(file_hash);
CREATE INDEX idx_dataextract_jobs_document_id ON dataextract_jobs(document_id);
CREATE INDEX idx_dataextract_jobs_status ON dataextract_jobs(status);
CREATE INDEX idx_dataextract_jobs_job_id ON dataextract_jobs(job_id);
```

#### Tag 13-14: Model Updates
```python
# backend/app/models/dataextract.py
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.app.core.database import Base

class DocumentExtractionResult(Base):
    __tablename__ = "document_extraction_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    extraction_service = Column(String(50), default="dataextract")
    extracted_text = Column(Text)
    structured_data = Column(JSON)
    metadata = Column(JSON)
    processing_time_ms = Column(Integer)
    file_hash = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="extraction_results")

class DataExtractJob(Base):
    __tablename__ = "dataextract_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    job_id = Column(String(255))
    status = Column(String(50), default="pending")
    priority = Column(Integer, default=0)
    options = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Relationships
    document = relationship("Document", back_populates="dataextract_jobs")
```

### Woche 3-4: API Integration

#### Tag 15-17: API Endpoints
```python
# backend/app/api/v1/endpoints/dataextract.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.auth import get_current_user
from backend.app.models.user import User
from backend.app.services.dataextract_service import DataExtractService
from backend.app.services.knowledge_service import KnowledgeService

router = APIRouter()
dataextract_service = DataExtractService()

@router.post("/documents/{document_id}/extract")
async def extract_document_with_dataextract(
    document_id: str,
    include_metadata: bool = Form(True),
    include_text: bool = Form(True),
    include_structure: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Extrahiert Dokument mit DataExtract Service"""
    try:
        # Dokument laden und Berechtigung prüfen
        knowledge_service = KnowledgeService(db)
        document = knowledge_service.get_document(document_id, current_user.id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Datei-Inhalt laden
        file_path = document.file_path
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # DataExtract Service aufrufen
        options = {
            "include_metadata": include_metadata,
            "include_text": include_text,
            "include_structure": include_structure
        }
        
        result = await dataextract_service.extract_file(
            file_content, 
            document.file_name,
            options
        )
        
        # Ergebnis in Datenbank speichern
        # TODO: Implementierung
        
        return {
            "success": True,
            "document_id": document_id,
            "extraction_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/batch-extract")
async def batch_extract_documents(
    document_ids: List[str],
    include_metadata: bool = Form(True),
    include_text: bool = Form(True),
    include_structure: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Batch-Extraktion mehrerer Dokumente"""
    try:
        knowledge_service = KnowledgeService(db)
        results = []
        
        for document_id in document_ids:
            document = knowledge_service.get_document(document_id, current_user.id)
            if not document:
                continue
            
            # Asynchrone Verarbeitung starten
            job_id = await dataextract_service.extract_file_async(
                file_content=open(document.file_path, 'rb').read(),
                filename=document.file_name,
                options={
                    "include_metadata": include_metadata,
                    "include_text": include_text,
                    "include_structure": include_structure
                }
            )
            
            results.append({
                "document_id": document_id,
                "job_id": job_id,
                "status": "started"
            })
        
        return {
            "success": True,
            "jobs": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/extraction/formats")
async def get_supported_formats():
    """Gibt unterstützte Dateiformate zurück"""
    try:
        formats = await dataextract_service.get_supported_formats()
        return formats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/extraction/jobs/{job_id}")
async def get_extraction_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Abfragt Status eines Extraktions-Jobs"""
    try:
        status = await dataextract_service.get_job_status(job_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Tag 18-19: Service Integration
```python
# backend/app/services/knowledge_service.py erweitern
class KnowledgeService:
    def __init__(self, db=None):
        self.db = db
        self.dataextract_service = DataExtractService()
    
    async def process_document_with_dataextract(self, document_id: str) -> bool:
        """Verarbeitet Dokument mit DataExtract Service"""
        try:
            document = self.get_document(document_id)
            if not document:
                return False
            
            # Datei-Inhalt laden
            with open(document.file_path, 'rb') as f:
                file_content = f.read()
            
            # DataExtract Service aufrufen
            result = await self.dataextract_service.extract_file(
                file_content,
                document.file_name
            )
            
            # Ergebnis verarbeiten und speichern
            await self._save_extraction_result(document_id, result)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing document {document_id} with DataExtract: {e}")
            return False
    
    async def _save_extraction_result(self, document_id: str, result: dict):
        """Speichert Extraktionsergebnis in Datenbank"""
        # TODO: Implementierung
        pass
```

### Woche 4-5: Testing & Validation

#### Tag 20-22: Unit Tests
```python
# tests/test_dataextract_integration.py
import pytest
import httpx
from unittest.mock import AsyncMock, patch
from backend.app.services.dataextract_service import DataExtractService

class TestDataExtractService:
    @pytest.fixture
    def dataextract_service(self):
        return DataExtractService()
    
    @pytest.mark.asyncio
    async def test_extract_file_success(self, dataextract_service):
        """Test erfolgreiche Datei-Extraktion"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "success": True,
                "extracted_text": "Test content",
                "metadata": {"pages": 1}
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            result = await dataextract_service.extract_file(
                b"test content",
                "test.pdf"
            )
            
            assert result["success"] is True
            assert result["extracted_text"] == "Test content"
    
    @pytest.mark.asyncio
    async def test_extract_file_api_error(self, dataextract_service):
        """Test API-Fehler bei Extraktion"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = httpx.HTTPError("API Error")
            
            with pytest.raises(httpx.HTTPError):
                await dataextract_service.extract_file(
                    b"test content",
                    "test.pdf"
                )
```

#### Tag 23-24: Integration Tests
```python
# tests/integration/test_dataextract_workflow.py
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

class TestDataExtractWorkflow:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_extract_document_endpoint(self, client):
        """Test Dokument-Extraktion Endpoint"""
        # TODO: Implementierung mit Mock DataExtract Service
        pass
    
    def test_batch_extraction_endpoint(self, client):
        """Test Batch-Extraktion Endpoint"""
        # TODO: Implementierung
        pass
```

### Woche 5-6: Production Deployment

#### Tag 25-26: Environment Configuration
```bash
# .env erweitern
# DataExtract Configuration
DATAEXTRACT_URL=http://dataextract:8000
DATAEXTRACT_ENABLED=true
DATAEXTRACT_MAX_FILE_SIZE=157286400
DATAEXTRACT_WORKER_CONCURRENCY=4
DATAEXTRACT_ENABLE_OCR=true
DATAEXTRACT_ENABLE_MEDIA_EXTRACTION=true

# Feature Flags
USE_DATAEXTRACT=true
DATAEXTRACT_FALLBACK_ENABLED=true
```

#### Tag 27-28: Monitoring Setup
```python
# backend/app/monitoring/dataextract_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# DataExtract Metrics
dataextract_requests_total = Counter(
    'dataextract_requests_total',
    'Total number of DataExtract requests',
    ['method', 'status']
)

dataextract_processing_duration = Histogram(
    'dataextract_processing_duration_seconds',
    'DataExtract processing duration in seconds',
    ['file_type', 'file_size_bucket']
)

dataextract_active_jobs = Gauge(
    'dataextract_active_jobs',
    'Number of active DataExtract jobs'
)

dataextract_supported_formats = Gauge(
    'dataextract_supported_formats_total',
    'Total number of supported file formats'
)
```

#### Tag 29-30: Production Testing
```bash
# 1. Staging Environment Testen
docker-compose -f docker-compose.staging.yml up -d

# 2. Load Testing
# TODO: Implementierung mit locust oder ähnlichem Tool

# 3. Performance Monitoring
# TODO: Grafana Dashboards erstellen

# 4. Production Deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Konfigurationsdateien

### DataExtract Service Configuration
```python
# services/dataextract/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Service Configuration
    app_name: str = "DataExtract Service"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # API Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # File Processing
    max_file_size: int = 157286400  # 150MB
    upload_dir: str = "/app/uploads"
    temp_dir: str = "/app/temp"
    
    # Redis Configuration
    redis_url: str = "redis://redis:6379"
    
    # Processing Options
    enable_ocr: bool = True
    enable_media_extraction: bool = True
    worker_concurrency: int = 4
    
    # Monitoring
    enable_prometheus: bool = True
    enable_opentelemetry: bool = True
    
    class Config:
        env_file = ".env"
```

### Docker Compose Production
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  dataextract:
    image: convosphere/dataextract:latest
    ports:
      - "8001:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - MAX_FILE_SIZE=157286400
      - WORKER_CONCURRENCY=4
      - ENABLE_OCR=true
      - ENABLE_MEDIA_EXTRACTION=true
      - ENVIRONMENT=production
    volumes:
      - dataextract_uploads:/app/uploads
      - dataextract_temp:/app/temp
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - convosphere-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'

volumes:
  dataextract_uploads:
  dataextract_temp:

networks:
  convosphere-network:
    external: true
```

## 📊 Monitoring Dashboards

### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "DataExtract Service Metrics",
    "panels": [
      {
        "title": "Extraction Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(dataextract_requests_total[5m])",
            "legendFormat": "{{method}}"
          }
        ]
      },
      {
        "title": "Processing Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(dataextract_processing_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Jobs",
        "type": "stat",
        "targets": [
          {
            "expr": "dataextract_active_jobs"
          }
        ]
      }
    ]
  }
}
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Alle Tests bestanden
- [ ] Code Review abgeschlossen
- [ ] Docker Images gebaut und getestet
- [ ] Monitoring konfiguriert
- [ ] Backup-Strategie implementiert
- [ ] Rollback-Plan erstellt

### Deployment
- [ ] Staging Environment deployed
- [ ] End-to-End Tests erfolgreich
- [ ] Performance Tests bestanden
- [ ] Production Environment deployed
- [ ] Monitoring aktiviert
- [ ] Team informiert

### Post-Deployment
- [ ] Service Health überwacht
- [ ] Performance-Metriken gesammelt
- [ ] User Feedback eingeholt
- [ ] Documentation aktualisiert
- [ ] Support-Prozesse definiert

---

**Nächste Schritte**: 
1. Repository Setup und Code Review
2. Docker Configuration
3. Service Integration
4. Testing und Validation
5. Production Deployment