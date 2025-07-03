# Docker Deployment

## Overview

This guide describes how to deploy the AI Assistant Platform using Docker and docker-compose for both backend and frontend components.

---

## Prerequisites
- Docker (v20+ empfohlen)
- docker-compose (v2+ empfohlen)
- Optional: .env Datei für Umgebungsvariablen

---

## Directory Structure
```
docker/
  backend/Dockerfile
  frontend/Dockerfile
  nginx/
    nginx.conf
    conf.d/default.conf
  postgres/init.sql
docker-compose.yml
```

---

## Backend Dockerfile (Beispiel)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY backend/main.py ./main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Frontend Dockerfile (Beispiel)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY frontend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY frontend/ ./
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## docker-compose.yml (Ausschnitt)
```yaml
version: '3.8'
services:
  backend:
    build: ./docker/backend
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - weaviate
  frontend:
    build: ./docker/frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: chatuser
      POSTGRES_PASSWORD: chatpass
      POSTGRES_DB: chatdb
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  weaviate:
    image: semitechnologies/weaviate:1.22.3
    ports:
      - "8080:8080"
    environment:
      - QUERY_DEFAULTS_LIMIT=25
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
volumes:
  pgdata:
```

---

## Environment Variables (.env Beispiel)
```
SECRET_KEY=supersecret
DATABASE_URL=postgresql+asyncpg://chatuser:chatpass@postgres:5432/chatdb
REDIS_URL=redis://redis:6379
WEAVIATE_URL=http://weaviate:8080
OPENAI_API_KEY=sk-...
```

---

## Healthchecks
- **Backend:** `GET /api/v1/health` (liefert `{ "status": "healthy" }`)
- **Frontend:** Streamlit-Startseite erreichbar unter Port 8501
- **Postgres:** Port 5432 offen, DB erreichbar
- **Redis:** Port 6379 offen
- **Weaviate:** Port 8080 offen, `/v1/.well-known/ready` liefert Status

---

## Starten
```bash
docker-compose up --build
```

---

## Tipps
- Passe die Ports bei Bedarf an.
- Für Produktion: sichere .env und setze `DEBUG` auf `False`.
- Nutze `docker-compose logs -f` für Logs.
- Nutze `docker-compose down -v` zum Stoppen und Entfernen aller Daten.

---

## Weiterführende Links
- [Docker Compose Doku](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Streamlit Deployment](https://docs.streamlit.io/) 