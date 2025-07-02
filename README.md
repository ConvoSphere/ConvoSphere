# AI Assistant Platform

A comprehensive AI assistant platform built with Python, featuring multiple assistants with personality profiles, extensive tool support, and enterprise-grade features.

## 🚀 Features

- **Multi-Assistant Support**: Create and manage multiple AI assistants with unique personalities
- **Extensive Tool Ecosystem**: Modular tool architecture supporting 50+ tools
- **Enterprise Security**: RBAC (Role-Based Access Control) with audit logging
- **Multi-language Support**: Internationalization (i18n) for UI and assistant responses
- **Semantic Search**: Weaviate integration for intelligent content retrieval
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

- **Backend**: Python 3.11+, FastAPI, Pydantic
- **AI/LLM**: LiteLLM, OpenAI, Anthropic, Local Models
- **Frontend**: NiceGUI, Vue.js components
- **Database**: PostgreSQL 15+, Redis
- **Vector Search**: Weaviate
- **Authentication**: JWT, OAuth2
- **Containerization**: Docker, Docker Compose

## 📦 Installation

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd chatassistant

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Start with Docker
docker-compose up -d

# Or run locally
pip install -r requirements.txt
python -m backend.main
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/chatassistant
REDIS_URL=redis://localhost:6379

# AI Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Weaviate
WEAVIATE_URL=http://localhost:8080

# Security
SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Tool Development Guide](docs/tools.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guidelines](docs/contributing.md)

## 🎯 Roadmap

- [x] Project structure setup
- [ ] Core backend implementation
- [ ] Frontend UI development
- [ ] Tool system implementation
- [ ] RBAC integration
- [ ] Multi-language support
- [ ] Testing suite
- [ ] Documentation
- [ ] Production deployment

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.