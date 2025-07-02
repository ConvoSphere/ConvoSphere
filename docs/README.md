# ChatAssistant Platform

A comprehensive AI assistant platform with advanced document processing capabilities, built with Python, FastAPI, NiceGUI, and modern AI technologies.

## Features

### Core Platform
- **Multi-Assistant Support**: Create and manage multiple AI assistants with different personalities and capabilities
- **Real-time Chat**: WebSocket-based real-time chat interface with streaming responses
- **Tool Integration**: Extensible tool system with MCP (Model Context Protocol) support
- **Knowledge Base**: Advanced document processing and semantic search with RAG capabilities
- **User Management**: Role-based access control (RBAC) with JWT authentication
- **Multilingual Support**: Internationalization (i18n) support for multiple languages

### Advanced Document Processing
- **Docling Integration**: Advanced document processing with OCR, ASR, and vision models
- **Multiple Processing Engines**: Support for traditional and Docling processing engines
- **Intelligent Chunking**: Context-aware document chunking with metadata preservation
- **Table & Figure Extraction**: Automatic extraction of tables, figures, and formulas
- **Page Layout Understanding**: Advanced layout analysis for complex documents
- **Audio Transcription**: Automatic speech recognition (ASR) for audio files
- **Image Analysis**: Vision model integration for image content analysis

### AI Capabilities
- **LiteLLM Integration**: Unified interface for multiple LLM providers
- **Semantic Search**: Vector-based search using Weaviate
- **RAG (Retrieval-Augmented Generation)**: Enhanced responses with knowledge base context
- **Streaming Responses**: Real-time streaming of AI responses
- **Context Management**: Intelligent conversation context handling

### Security & Performance
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Granular permissions system
- **Database Security**: SQLAlchemy with PostgreSQL
- **API Rate Limiting**: Built-in rate limiting and throttling
- **Error Handling**: Comprehensive error handling and logging

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Weaviate**: Vector database for semantic search
- **LiteLLM**: Unified LLM interface
- **Docling**: Advanced document processing
- **Pydantic**: Data validation and settings management
- **Alembic**: Database migrations

### Frontend
- **NiceGUI**: Modern Python web framework for building UIs
- **WebSocket**: Real-time communication
- **Tailwind CSS**: Utility-first CSS framework
- **Internationalization**: Multi-language support

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and load balancer
- **PostgreSQL**: Database container

## Quick Start

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chatassistant.git
   cd chatassistant
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r frontend/requirements.txt
   ```

2. **Set up database**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Start services**
   ```bash
   # Terminal 1: Backend
   cd backend
   python main.py
   
   # Terminal 2: Frontend
   cd frontend
   python main.py
   ```

## Advanced Document Processing with Docling

The platform includes advanced document processing capabilities powered by Docling:

### Supported Formats
- **Documents**: PDF, DOCX, TXT, MD, HTML
- **Images**: JPG, PNG, TIFF, BMP
- **Audio**: MP3, WAV, M4A, FLAC
- **Video**: MP4, AVI, MOV (audio extraction)

### Processing Features
- **OCR (Optical Character Recognition)**: Extract text from scanned documents and images
- **ASR (Automatic Speech Recognition)**: Transcribe audio files to text
- **Vision Models**: Analyze image content and extract information
- **Table Extraction**: Identify and extract structured data from tables
- **Figure Recognition**: Detect and analyze figures, charts, and diagrams
- **Formula Recognition**: Extract mathematical formulas and equations
- **Page Layout Analysis**: Understand document structure and formatting

### Usage

#### Basic Upload
```python
# Simple document upload
document = await knowledge_service.upload_document(file_data, metadata)
```

#### Advanced Upload with Docling
```python
# Advanced upload with specific processing options
document = await knowledge_service.upload_document_advanced(
    file_data,
    metadata,
    engine="docling",
    processing_options={
        "ocr": True,
        "asr": True,
        "vision": True,
        "tables": True,
        "figures": True
    }
)
```

#### Document Reprocessing
```python
# Reprocess document with different engine
success = await knowledge_service.reprocess_document(
    document_id,
    engine="docling",
    processing_options={"ocr": True, "tables": True}
)
```

### API Endpoints

#### Processing Engines
- `GET /api/v1/knowledge/processing/engines` - Get available processing engines
- `GET /api/v1/knowledge/processing/supported-formats` - Get supported formats

#### Advanced Upload
- `POST /api/v1/knowledge/documents/upload-advanced` - Upload with processing options
- `POST /api/v1/knowledge/documents/{id}/reprocess` - Reprocess document

## API Documentation

### Authentication
All API endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh token

#### Assistants
- `GET /api/v1/assistants` - List assistants
- `POST /api/v1/assistants` - Create assistant
- `GET /api/v1/assistants/{id}` - Get assistant details

#### Conversations
- `GET /api/v1/conversations` - List conversations
- `POST /api/v1/conversations` - Create conversation
- `GET /api/v1/conversations/{id}/messages` - Get conversation messages

#### Knowledge Base
- `GET /api/v1/knowledge/documents` - List documents
- `POST /api/v1/knowledge/documents/upload` - Upload document
- `POST /api/v1/knowledge/documents/upload-advanced` - Advanced upload
- `GET /api/v1/knowledge/search` - Search knowledge base

#### Tools
- `GET /api/v1/tools` - List available tools
- `POST /api/v1/tools` - Create custom tool

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/chatassistant

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
LITELLM_API_KEY=your-litellm-key
DEFAULT_LLM_MODEL=gpt-3.5-turbo
DEFAULT_EMBEDDING_MODEL=text-embedding-ada-002

# Weaviate
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your-weaviate-key

# Docling
DOCLING_API_KEY=your-docling-key
DOCLING_MODEL=docling-v2.39.0

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
```

### Docker Configuration

The platform includes Docker configurations for easy deployment:

- `docker-compose.yml` - Main orchestration file
- `docker/backend/Dockerfile` - Backend container
- `docker/frontend/Dockerfile` - Frontend container
- `docker/nginx/` - Nginx configuration
- `docker/postgres/` - Database initialization

## Development

### Project Structure
```
chatassistant/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   ├── core/           # Core configuration
│   │   │   ├── models/         # Database models
│   │   │   ├── services/       # Business logic
│   │   │   ├── schemas/        # Pydantic schemas
│   │   │   └── tools/          # Tool implementations
│   │   ├── alembic/            # Database migrations
│   │   └── tests/              # Backend tests
│   ├── frontend/               # NiceGUI frontend
│   │   ├── components/         # UI components
│   │   ├── pages/             # Page implementations
│   │   ├── services/          # Frontend services
│   │   └── i18n/              # Internationalization
│   ├── docker/                # Docker configurations
│   └── docs/                  # Documentation
└── scripts/               # Utility scripts
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests (if implemented)
cd frontend
pytest
```

### Code Quality
```bash
# Format code
black backend/ frontend/

# Lint code
flake8 backend/ frontend/

# Type checking
mypy backend/ frontend/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`

## Roadmap

- [ ] Enhanced MCP tool support
- [ ] Advanced analytics and reporting
- [ ] Multi-tenant architecture
- [ ] Advanced caching strategies
- [ ] Performance optimizations
- [ ] Additional AI model integrations
- [ ] Mobile application
- [ ] Advanced workflow automation 