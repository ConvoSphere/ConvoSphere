# Knowledge Base Feature

## Overview

The Knowledge Base allows users and assistants to upload, store, search, and retrieve documents and structured knowledge. It supports semantic search using embeddings and integrates with the Weaviate vector database.

---

## Features
- **Document Upload**: Users can upload PDFs, text, and other supported files.
- **Automatic Embedding**: Uploaded documents are automatically chunked and embedded using AI models.
- **Semantic Search**: Fast, context-aware search over all knowledge items.
- **Knowledge Management**: CRUD operations for documents and metadata.
- **Access Control**: User-based permissions for private and shared knowledge.

---

## Architecture
- **Backend**: FastAPI, SQLAlchemy, Weaviate
- **Frontend**: Streamlit components for upload, search, and display
- **Embeddings**: Generated via OpenAI, local models, or other providers

---

## Document Upload
```python
# Endpoint: POST /api/v1/knowledge/upload
# Accepts: multipart/form-data (file, metadata)
# Stores file, extracts text, creates embeddings
```

---

## Embedding & Chunking
- Documents are split into manageable chunks (z.B. 500 Tokens)
- Each chunk is embedded and stored in Weaviate
- Metadata (title, author, tags) wird mitgespeichert

---

## Semantic Search
```python
# Endpoint: POST /api/v1/knowledge/search
# Body: { "query": "What is vector search?" }
# Returns: List of relevant document chunks with context
```
- Uses vector similarity in Weaviate
- Supports filters (user, tags, date)

---

## Access Control
- Private: Nur Besitzer kann Dokument sehen
- Shared: Mit bestimmten Nutzern oder Teams teilbar
- Public: Optional, für alle sichtbar

---

## Beispiel-Workflow
1. User lädt PDF hoch
2. Backend extrahiert Text, chunked, erstellt Embeddings
3. Chunks werden in Weaviate gespeichert
4. User sucht nach Begriff → semantisch relevante Abschnitte werden angezeigt

---

## Best Practices
- Nutze sprechende Titel und Tags
- Halte Dokumente aktuell
- Prüfe Zugriffsrechte regelmäßig 