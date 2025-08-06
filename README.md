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

**Ready to dive deeper?** Check out our [📚 Documentation](docs/index.md) for detailed guides, including [SSO Setup](docs/SSO_SETUP.md), [Knowledge Base Settings](docs/KNOWLEDGE_BASE_SETTINGS.md), and [Security Setup](docs/security/setup.md).

## ✨ Key Features

### Core Capabilities
- **Enterprise SSO**: Comprehensive Single Sign-On with Google, Microsoft, GitHub, SAML, and OIDC
- **Advanced Knowledge Management**: Document processing with configurable chunking, embedding models, and semantic search
- **AI Assistant Platform**: Create and manage custom AI assistants with different personalities and capabilities
- **Real-time Chat**: WebSocket-based messaging with instant delivery and file attachments
- **AI Integration**: Powered by LiteLLM with support for multiple AI providers (OpenAI, Anthropic, Google)
- **User Authentication**: JWT-based authentication with role-based access control (User, Admin, Super Admin)
- **Document Processing**: Support for PDF, DOCX, TXT, MD with AI-powered metadata extraction
- **Conversation Intelligence**: Advanced analytics and insights from conversations
- **Tool Integration**: MCP (Model Context Protocol) tools and custom tool management
- **Responsive Design**: Modern UI with dark/light theme support and accessibility features

### Advanced Features
- **Knowledge Base Settings**: Configurable document processing, embedding models, and search algorithms
- **Conversation Analytics**: Sentiment analysis, topic clustering, and user behavior insights
- **Domain Groups**: Enterprise user management with LDAP/AD integration
- **Export & Backup**: Comprehensive data export and backup capabilities
- **Performance Monitoring**: Real-time system health monitoring and alerting
- **Rate Limiting**: API protection with configurable limits
- **Audit Logging**: Complete audit trail for compliance and security

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
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **PostgreSQL**: Primary database for user data and conversations
- **Redis**: Caching and session storage
- **Weaviate**: Vector database for semantic search
- **LiteLLM**: AI provider abstraction layer

### Frontend
- **React 18**: Modern React with TypeScript and concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Zustand**: Lightweight state management
- **Ant Design**: Enterprise UI component library with modern design system
- **React Router**: Client-side routing with protected routes
- **WebSocket**: Real-time communication
- **i18next**: Internationalization (EN/DE)
- **Modern UI Components**: Custom ModernCard, ModernButton, ModernInput components
- **Performance Monitoring**: Real-time performance tracking

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

### Quick Setup with Docker (Recommended)

```bash
# Clone and start
git clone <repository-url>
cd convosphere
docker-compose up --build
```

### Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend-react
npm install
cp .env.example .env
# Edit .env with your backend API URL
npm start
```

## 🧪 Testing

### Backend Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_auth.py
pytest tests/test_performance.py
```

### Frontend Testing
```bash
# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run cypress:run
```

## 📊 Performance Metrics

### Backend Performance
- **Response Time**: < 100ms for health checks, < 500ms for API calls
- **Concurrent Users**: Supports 100+ concurrent connections
- **Memory Usage**: < 50MB increase under load
- **Database Queries**: Optimized with connection pooling
- **File Upload**: Handles 1MB+ files efficiently

### Frontend Performance
- **Page Load**: < 3 seconds for initial load
- **Bundle Size**: Optimized with code splitting
- **Real-time Updates**: < 100ms message delivery
- **Memory Management**: Efficient component lifecycle
- **Accessibility**: WCAG 2.1 AA compliant

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/convosphere

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# SSO Configuration
SSO_GOOGLE_ENABLED=false
SSO_GOOGLE_CLIENT_ID=your-google-client-id
SSO_GOOGLE_CLIENT_SECRET=your-google-client-secret
SSO_GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/sso/callback/google

SSO_MICROSOFT_ENABLED=false
SSO_MICROSOFT_CLIENT_ID=your-microsoft-client-id
SSO_MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

SSO_GITHUB_ENABLED=false
SSO_GITHUB_CLIENT_ID=your-github-client-id
SSO_GITHUB_CLIENT_SECRET=your-github-client-secret

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# External Services
WEAVIATE_URL=http://localhost:8080
REDIS_URL=redis://localhost:6379

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_ENVIRONMENT=development
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment
```bash
# Backend
cd backend
pip install -r requirements.txt
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd frontend-react
npm run build
serve -s build -l 8081
```

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

### Key Endpoints
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/auth/sso/providers` - List SSO providers
- `POST /api/v1/chat/messages` - Send chat message
- `GET /api/v1/conversations/` - List conversations
- `POST /api/v1/knowledge/upload` - Upload documents
- `GET /api/v1/knowledge/settings` - Knowledge base settings
- `POST /api/v1/search` - Semantic search
- `GET /api/v1/admin/users` - Admin user management
- `GET /health` - Health check

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Enterprise SSO integration (Google, Microsoft, GitHub, SAML, OIDC)
- Role-based access control (User, Admin, Super Admin)
- Password hashing with bcrypt
- Rate limiting on API endpoints
- CORS configuration for cross-origin requests

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- File upload validation
- Secure headers configuration

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues
```bash
# Database connection issues
pytest tests/test_config.py

# Import errors
python -c "from app.core.config import settings; print(settings)"

# Memory issues
pytest tests/test_performance.py::TestPerformance::test_memory_usage_under_load
```

#### Frontend Issues
```bash
# Build errors
npm run build

# Test failures
npm test -- --verbose

# E2E test issues
npx cypress run --headed
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `npm test && pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Quality
- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/TypeScript
- Maintain test coverage above 90%
- Write meaningful commit messages
- Update documentation for new features

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