# Developer Guide - ConvoSphere entwickeln

## 🎯 Übersicht

ConvoSphere ist eine moderne AI-Chat-Plattform mit FastAPI Backend und React Frontend. Dieser Guide hilft Entwicklern, das System zu verstehen, zu erweitern und zu deployen.

## 🏗️ Architektur

### System-Übersicht
```mermaid
graph TB
    subgraph "Frontend (React/TypeScript)"
        UI[React UI]
        WS[WebSocket Client]
        State[Zustand State]
    end
    
    subgraph "Backend (FastAPI)"
        API[REST API]
        WS_Server[WebSocket Server]
        Auth[JWT Auth]
        AI[AI Services]
        KB[Knowledge Base]
        MCP[MCP Tools]
    end
    
    subgraph "Daten"
        PG[(PostgreSQL)]
        Redis[(Redis)]
        Weaviate[(Weaviate)]
    end
    
    UI --> API
    UI --> WS_Server
    API --> Auth
    API --> AI
    API --> KB
    API --> MCP
    AI --> Weaviate
    KB --> Weaviate
```

### Technologie-Stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Redis, Weaviate
- **Frontend**: React 18, TypeScript, Ant Design, Zustand
- **AI**: LiteLLM, OpenAI, Anthropic
- **Deployment**: Docker, Docker Compose

## 🚀 Development Setup

### Voraussetzungen
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 14+**
- **Redis 6+**
- **Docker & Docker Compose**

### Schneller Start (Docker)
```bash
# Repository klonen
git clone https://github.com/your-org/convosphere.git
cd convosphere

# Mit Docker starten
docker-compose up --build

# Services verfügbar:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manueller Setup

#### Backend Setup
```bash
# Backend-Verzeichnis
cd backend

# Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Dependencies
pip install -r requirements.txt

# Environment
cp env.example .env
# .env bearbeiten mit lokalen Einstellungen

# Datenbank
alembic upgrade head

# Starten
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
# Frontend-Verzeichnis
cd frontend-react

# Dependencies
npm install

# Environment
cp .env.example .env.local
# .env.local bearbeiten

# Starten
npm run dev
```

## 📁 Projekt-Struktur

```
convosphere/
├── backend/
│   ├── app/
│   │   ├── api/           # API-Endpunkte
│   │   ├── core/          # Konfiguration, Sicherheit
│   │   ├── models/        # Datenbank-Modelle
│   │   ├── schemas/       # Pydantic-Schemas
│   │   ├── services/      # Business Logic
│   │   └── utils/         # Utilities
│   ├── alembic/           # Datenbank-Migrationen
│   └── tests/             # Tests
├── frontend-react/
│   ├── src/
│   │   ├── components/    # React-Komponenten
│   │   ├── pages/         # Seiten-Komponenten
│   │   ├── services/      # API-Services
│   │   ├── store/         # Zustand State
│   │   └── utils/         # Utilities
│   └── public/            # Statische Assets
├── docs/                  # Dokumentation
└── docker/                # Docker-Konfiguration
```

## 🔧 Entwicklung

### Code-Stil
- **Python**: Black, isort, flake8
- **TypeScript**: ESLint, Prettier
- **Pre-commit Hooks**: Automatische Formatierung

### Tests
```bash
# Backend Tests
cd backend
pytest

# Frontend Tests
cd frontend-react
npm test

# E2E Tests
npm run test:e2e
```

### Datenbank-Migrationen
```bash
# Neue Migration erstellen
alembic revision --autogenerate -m "Description"

# Migration ausführen
alembic upgrade head

# Migration rückgängig
alembic downgrade -1
```

### API-Entwicklung
```python
# Neuer Endpunkt
@router.post("/custom-endpoint")
async def custom_endpoint(
    request: CustomRequest,
    current_user: User = Depends(get_current_user)
) -> CustomResponse:
    """Custom endpoint description"""
    # Implementation
    return CustomResponse(data=result)
```

## 🔌 API Reference

### Authentifizierung
```python
# JWT Token erhalten
POST /api/v1/auth/login
{
    "email": "user@example.com",
    "password": "password"
}

# Token verwenden
Authorization: Bearer <token>
```

### Haupt-Endpunkte

#### Chat
- `POST /api/v1/chat/messages` - Nachricht senden
- `GET /api/v1/chat/conversations` - Konversationen abrufen
- `DELETE /api/v1/chat/conversations/{id}` - Konversation löschen

#### Knowledge Base
- `POST /api/v1/knowledge/documents` - Dokument hochladen
- `GET /api/v1/knowledge/documents` - Dokumente abrufen
- `POST /api/v1/knowledge/search` - Dokumente durchsuchen

#### Users
- `GET /api/v1/users/me` - Eigenes Profil
- `PUT /api/v1/users/me` - Profil aktualisieren
- `POST /api/v1/users` - Benutzer erstellen (Admin)

### WebSocket
```javascript
// Verbindung
const ws = new WebSocket('ws://localhost:8000/ws');

// Nachricht senden
ws.send(JSON.stringify({
    type: 'message',
    content: 'Hello',
    conversation_id: 1
}));

// Nachrichten empfangen
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

## 🛠️ Custom Tools (MCP)

### Tool erstellen
```python
# backend/app/tools/custom_tool.py
from mcp import Tool

class CustomTool(Tool):
    name = "custom_tool"
    description = "Custom tool description"
    
    async def execute(self, params: dict) -> dict:
        # Tool-Logik
        result = self.process(params)
        return {"result": result}
    
    def process(self, params: dict) -> str:
        # Implementation
        return "Tool result"
```

### Tool registrieren
```python
# backend/app/main.py
from app.tools.custom_tool import CustomTool

# Tool zur Registry hinzufügen
tool_registry.register(CustomTool())
```

## 🔒 Sicherheit

### JWT Authentication
```python
# Token erstellen
token = create_access_token(data={"sub": user.email})

# Token validieren
user = get_current_user(token)
```

### Rate Limiting
```python
# Endpunkt mit Rate Limiting
@limiter.limit("100/minute")
@router.post("/api/v1/endpoint")
async def rate_limited_endpoint():
    pass
```

### Input Validation
```python
# Pydantic Schema
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(max_length=100)
```

## 📊 Monitoring & Logging

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Log-Level
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Metrics
```python
# Prometheus Metrics
from prometheus_client import Counter, Histogram

request_counter = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
```

### Health Checks
```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## 🚀 Deployment

### Docker Production
```bash
# Production Build
docker-compose -f docker-compose.prod.yml up -d

# Environment
cp env.example .env.prod
# Production-Einstellungen konfigurieren
```

### Environment Variables
```bash
# Backend
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
SECRET_KEY=your-secret-key
AI_PROVIDER_API_KEY=your-api-key

# Frontend
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com
```

### Production Checklist
- [ ] **Environment** konfiguriert
- [ ] **SSL/TLS** eingerichtet
- [ ] **Backup-Strategie** implementiert
- [ ] **Monitoring** aktiviert
- [ ] **Logs** zentralisiert
- [ ] **Security Headers** gesetzt
- [ ] **Rate Limiting** aktiviert

## 🧪 Testing

### Unit Tests
```python
# backend/tests/test_service.py
import pytest
from app.services.user_service import UserService

def test_create_user():
    service = UserService()
    user = service.create_user("test@example.com", "password")
    assert user.email == "test@example.com"
```

### Integration Tests
```python
# backend/tests/test_api.py
from fastapi.testclient import TestClient

def test_login(client: TestClient):
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    assert response.status_code == 200
```

### E2E Tests
```javascript
// frontend-react/cypress/e2e/chat.cy.js
describe('Chat', () => {
  it('should send a message', () => {
    cy.visit('/chat')
    cy.get('[data-testid="message-input"]').type('Hello')
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="message"]').should('contain', 'Hello')
  })
})
```

## 🔄 CI/CD

### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI/CD
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend && pytest
          cd frontend-react && npm test
```

### Docker Build
```dockerfile
# Dockerfile.prod
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📚 Ressourcen

### Dokumentation
- **[API Docs](http://localhost:8000/docs)** - Interaktive API-Dokumentation
- **[ReDoc](http://localhost:8000/redoc)** - Alternative API-Docs
- **[Architecture](architecture.md)** - Detaillierte Architektur

### Community
- **[GitHub Issues](https://github.com/your-org/convosphere/issues)** - Bug Reports
- **[Discussions](https://github.com/your-org/convosphere/discussions)** - Fragen & Feedback
- **[Discord](https://discord.gg/your-server)** - Community Support

### Tools
- **[Postman Collection](https://github.com/your-org/convosphere/tree/main/docs/postman)** - API Testing
- **[Docker Images](https://hub.docker.com/r/your-org/convosphere)** - Container Images

---

**Weitere Hilfe?** [API Reference](api-reference.md) | [Deployment](deployment.md) | [FAQ](faq.md)