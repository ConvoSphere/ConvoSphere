# AI Assistant Platform

A comprehensive AI assistant platform built with Python, featuring multiple assistants with personality profiles, extensive tool support, and enterprise-grade features.

## 🚀 Features

- **Multi-Assistant Support**: Create and manage multiple AI assistants with unique personalities
- **Extensive Tool Ecosystem**: Modular tool architecture supporting MCP (Model Context Protocol) tools
- **Enterprise Security**: RBAC (Role-Based Access Control) with audit logging
- **Multi-language Support**: Internationalization (i18n) for UI and assistant responses
- **Semantic Search**: Weaviate integration for intelligent content retrieval and RAG
- **Knowledge Base**: Document upload, processing, and semantic search
- **Real-time Chat**: WebSocket-based real-time conversations
- **Modern UI**: NiceGUI-based responsive web interface
- **Scalable Architecture**: Microservices-ready with PostgreSQL and Redis

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   NiceGUI       │    │   FastAPI       │    │   PostgreSQL    │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Weaviate      │    │   LiteLLM       │
                       │   Vector DB     │    │   LLM Gateway   │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy
- **AI/LLM**: LiteLLM, OpenAI, Anthropic, Local Models
- **Frontend**: NiceGUI 2.20.0, Vue.js components
- **Database**: PostgreSQL 15+, Redis
- **Vector Search**: Weaviate
- **Authentication**: JWT, OAuth2
- **Document Processing**: PyPDF2, python-docx, textract
- **Embeddings**: Sentence Transformers, OpenAI Embeddings
- **Containerization**: Docker, Docker Compose

## 📦 Installation

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Quick Start with Docker

```bash
# Clone repository
git clone <repository-url>
cd chatassistant

# Setup environment
cp env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Local Development Setup

```bash
# Clone repository
git clone <repository-url>
cd chatassistant

# Setup Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

# Setup environment
cp env.example .env
# Edit .env with your configuration

# Start services
docker-compose up -d postgres redis weaviate

# Run backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run frontend (in another terminal)
cd frontend
python -m main
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Application
APP_NAME=AI Assistant Platform
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000
FRONTEND_PORT=3000

# Database
DATABASE_URL=postgresql://chatassistant:chatassistant_password@localhost:5432/chatassistant
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# Security
SECRET_KEY=your_super_secret_key_at_least_32_characters_long
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Providers
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key

# LiteLLM Configuration
LITELLM_MODEL=gpt-4
LITELLM_MAX_TOKENS=4096
LITELLM_TEMPERATURE=0.7

# Weaviate Configuration
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key

# Knowledge Base Configuration
DEFAULT_EMBEDDING_MODEL=text-embedding-ada-002
DEFAULT_CHUNK_SIZE=500
DEFAULT_CHUNK_OVERLAP=50
MAX_CHUNK_SIZE=2000
MIN_CHUNK_SIZE=100

# Document Processing
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_FILE_SIZE=10485760

# File Storage
UPLOAD_DIR=./uploads

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# Internationalization
DEFAULT_LANGUAGE=de
SUPPORTED_LANGUAGES=de,en,fr,es
```

## 🚀 Usage

### Starting the Application

1. **With Docker (Recommended)**:
   ```bash
   docker-compose up -d
   ```

2. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Key Features

1. **Authentication**: Register/login to access the platform
2. **Assistants**: Create and configure AI assistants with personalities
3. **Conversations**: Start real-time conversations with assistants
4. **Tools**: Use built-in tools and integrate MCP servers
5. **Knowledge Base**: Upload documents for RAG-powered responses
6. **Search**: Semantic search across conversations and knowledge base

## 📚 Documentation

- [API Documentation](docs/api.md)
- [MCP Integration Guide](docs/mcp_integration.md)
- [Tool Development Guide](docs/tools.md)
- [Deployment Guide](docs/deployment.md)

## 🎯 Project Status

### ✅ Completed Features
- [x] Project structure and architecture
- [x] Backend API with FastAPI
- [x] Database models and migrations
- [x] Authentication and RBAC
- [x] Assistant management
- [x] Conversation system
- [x] Real-time WebSocket chat
- [x] MCP tool integration
- [x] Knowledge base with document processing
- [x] Semantic search with Weaviate
- [x] Frontend with NiceGUI
- [x] Docker containerization

### 🔄 In Progress
- [ ] Advanced document processing (OCR, audio)
- [ ] Background task processing
- [ ] Advanced analytics and reporting
- [ ] Multi-tenant support
- [ ] Advanced security features

### 📋 Planned Features
- [ ] Mobile app support
- [ ] Advanced AI model integration
- [ ] Workflow automation
- [ ] Advanced analytics
- [ ] Enterprise SSO integration

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
pytest

# Run all tests
make test
```

## 🐛 Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in .env
   - Run database migrations: `alembic upgrade head`

2. **Weaviate connection errors**:
   - Ensure Weaviate is running
   - Check WEAVIATE_URL in .env
   - Verify Weaviate health: `curl http://localhost:8080/v1/.well-known/ready`

3. **Document processing errors**:
   - Ensure all system dependencies are installed
   - Check file permissions for uploads directory
   - Verify embedding model API keys

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs weaviate
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [NiceGUI](https://nicegui.io/) for the frontend framework
- [Weaviate](https://weaviate.io/) for vector search
- [LiteLLM](https://github.com/BerriAI/litellm) for LLM abstraction
- [MCP](https://modelcontextprotocol.io/) for tool integration