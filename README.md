# ConvoSphere

A modern, full-stack AI assistant platform built with **FastAPI** (Backend) and **React** (Frontend), featuring comprehensive SSO integration, advanced knowledge management, and enterprise-grade AI capabilities.

> **🚀 Production Ready**: This is a mature platform with enterprise features including SSO, advanced document processing, and comprehensive admin tools.

<div align="center">

![ConvoSphere](https://img.shields.io/badge/ConvoSphere-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

[![Documentation](https://img.shields.io/badge/Documentation-MkDocs-blue)](https://convosphere.github.io/convosphere/)
[![Tests](https://img.shields.io/badge/Tests-Passing-green)](https://github.com/ConvoSphere/ConvoSphere/actions)
[![Coverage](https://img.shields.io/badge/Coverage-90%25+-green)](https://github.com/ConvoSphere/ConvoSphere/actions)

</div>

## 🚀 Quick Start

Get up and running in under 10 minutes:

```bash
# Clone the repository
git clone https://github.com/ConvoSphere/ConvoSphere.git
cd convosphere

# Quick setup with Docker (recommended)
docker-compose up --build

# Or manual setup
make setup
make install
make dev
```

**Ready to dive deeper?** Check out our [📚 Documentation](docs/index.md) for detailed guides, including:

- **[Knowledge Base Settings](docs/KNOWLEDGE_BASE_SETTINGS.md)** - Configure document processing and RAG
- **[RAG Features](docs/RAG_FEATURES.md)** - Advanced retrieval-augmented generation
- **[Bulk Operations](docs/BULK_OPERATIONS.md)** - Efficient document management
- **[Storage Integration](docs/STORAGE_INTEGRATION.md)** - Cloud storage setup
- **[SSO Setup](docs/SSO_SETUP.md)** - Enterprise authentication
- **[Security Setup](docs/security/setup.md)** - Security configuration

## ✨ Key Features

- **🤖 AI Assistant Platform**: Create and manage custom AI assistants with different personalities
- **💬 Real-time Chat**: WebSocket-based messaging with file attachments and instant delivery
- **📚 Knowledge Management**: Document processing with semantic search and AI-powered insights
- **🔐 Enterprise SSO**: Comprehensive Single Sign-On (Google, Microsoft, GitHub, SAML, OIDC)
- **👥 User Management**: Role-based access control with enterprise features
- **🛠️ Tool Integration**: MCP (Model Context Protocol) tools and custom tool management
- **📊 Analytics**: Conversation intelligence and performance monitoring
- **🔒 Security**: Audit logging, rate limiting, and compliance features

> **📖 For detailed feature documentation, see our [User Guide](docs/user-guide.md)**

## 🏗️ Architecture

The application follows a **microservices-inspired** architecture with clear separation between frontend, backend, and external services.

```mermaid
graph TB
    subgraph "Frontend (React)"
        UI[React UI]
        WS[WebSocket Client]
        State[Zustand State]
    end
    
    subgraph "Backend (FastAPI)"
        API[REST API]
        WS_Server[WebSocket Server]
        Auth[JWT Auth]
        AI[AI Services]
        Search[Search Engine]
    end
    
    subgraph "External Services"
        AI_Providers[AI Providers<br/>OpenAI, Anthropic, etc.]
        Storage[File Storage]
        VectorDB[Vector Database]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL)]
        Redis[(Redis Cache)]
        Weaviate[(Weaviate)]
    end
    
    UI --> API
    UI --> WS_Server
    WS --> WS_Server
    API --> Auth
    API --> AI
    API --> Search
    AI --> AI_Providers
    Search --> VectorDB
    API --> PG
    API --> Redis
    Search --> Weaviate
    AI --> Storage
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** + **SQLAlchemy** + **PostgreSQL** - Modern web framework with ORM
- **Redis** + **Weaviate** - Caching and vector database for semantic search
- **LiteLLM** - AI provider abstraction (OpenAI, Anthropic, Google)

### Frontend
- **React 18** + **TypeScript** - Modern frontend with type safety
- **Ant Design** + **Zustand** - UI components and state management
- **WebSocket** + **i18next** - Real-time communication and internationalization

> **🔧 For detailed technical documentation, see our [Developer Guide](docs/developer-guide.md)**

### Development & Testing
- **Python 3.11+**: Backend programming language
- **Node.js 18+**: Frontend runtime
- **Pytest**: Python testing framework
- **Jest**: JavaScript testing framework
- **Cypress**: End-to-end testing
- **Docker**: Containerization and deployment

## 🚀 Installation

### Prerequisites
- Python 3.11+ (3.13, 3.12, 3.11 supported)
- Node.js 18+
- PostgreSQL 13+
- Git

### Quick Setup
```bash
# Clone and start
git clone https://github.com/ConvoSphere/ConvoSphere.git
cd ConvoSphere
docker-compose up --build
```

> **📖 For detailed installation instructions, see our [Quick Start Guide](docs/quick-start.md)**

## 🧪 Testing

```bash
# Backend tests
pytest

# Frontend tests
npm test

# With coverage
pytest --cov=app --cov-report=html
npm run test:coverage
```

> **🔧 For detailed testing information, see our [Developer Guide](docs/developer-guide.md)**

## 📊 Performance

- **Response Time**: < 500ms for API calls
- **Concurrent Users**: 100+ connections
- **File Upload**: Up to 50MB files
- **Real-time Updates**: < 100ms message delivery

> **📈 For detailed performance metrics, see our [Monitoring Documentation](docs/monitoring/)**

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/convosphere

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# External Services
WEAVIATE_URL=http://localhost:8080
REDIS_URL=redis://localhost:6379
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

> **🔧 For complete configuration options, see our [Configuration Guide](docs/configuration.md)**

## 🚀 Deployment

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up -d
```

> **🚀 For detailed deployment instructions, see our [Deployment Guide](docs/deployment.md)**

## 📚 Documentation

### Documentation Structure
Our documentation is organized into several categories:

- **📖 User Documentation**: User guides, quick start, and FAQ
- **🔧 Developer Documentation**: Architecture, API reference, and development guides
- **🔒 Security Documentation**: Security setup and best practices
- **📊 Reports**: Code quality reports, development progress, and analysis
- **📋 Changelog**: Version history and release notes

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

> **📖 For complete API documentation, see our [API Reference](docs/api.md)**

## 🔒 Security

- **JWT Authentication** with refresh tokens
- **Enterprise SSO** (Google, Microsoft, GitHub, SAML, OIDC)
- **Role-based Access Control** (User, Admin, Super Admin)
- **Rate Limiting** and **CORS** protection
- **Input Validation** and **SQL Injection** prevention

> **🔒 For detailed security information, see our [Security Guide](docs/security.md)**

## 🐛 Troubleshooting

```bash
# Common backend issues
pytest tests/test_config.py

# Common frontend issues
npm run build
npm test
```

> **🔧 For detailed troubleshooting, see our [FAQ](docs/faq.md)**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `npm test && pytest`
5. Commit and push your changes
6. Open a Pull Request

> **🤝 For detailed contribution guidelines, see our [Contributing Guide](docs/contributing.md)**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React team for the frontend framework
- Ant Design for the UI components
- LiteLLM for AI service integration
- Cypress for E2E testing framework
- All contributors and maintainers

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the [documentation](https://convosphere.github.io/convosphere/)
- Review the troubleshooting section
- Contact the development team

---

**Built with ❤️ by the AI Chat Team**