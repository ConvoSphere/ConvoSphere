# AI Chat Application

A modern, full-stack AI chat application built with FastAPI (Backend) and React (Frontend), featuring comprehensive test coverage, real-time messaging, and advanced AI capabilities.

## 🚀 Features

### Core Features
- **Real-time Chat**: WebSocket-based messaging with instant delivery
- **AI Integration**: Powered by LiteLLM with support for multiple AI providers
- **User Authentication**: JWT-based authentication with social login options
- **File Upload**: Support for PDF, DOCX, and text files with AI processing
- **Knowledge Base**: Document storage and semantic search capabilities
- **Conversation Management**: Organize and manage chat conversations
- **Responsive Design**: Mobile-first design with dark/light theme support

### Advanced Features
- **Voice Input**: Speech-to-text functionality
- **Message Formatting**: Markdown support with rich text editing
- **Search & Export**: Advanced search and conversation export
- **Performance Monitoring**: Real-time system health monitoring
- **Rate Limiting**: API protection against abuse
- **CORS Support**: Cross-origin resource sharing enabled

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with refresh mechanism
- **Real-time**: WebSocket connections for live messaging
- **AI Services**: LiteLLM integration for multiple AI providers
- **File Processing**: PDF, DOCX, and text file parsing
- **Search**: Vector-based semantic search with embeddings

### Frontend (React)
- **Framework**: React 18 with TypeScript
- **State Management**: Zustand for global state
- **UI Library**: Ant Design components
- **Routing**: React Router for navigation
- **Real-time**: WebSocket client for live updates
- **Testing**: Jest with React Testing Library
- **E2E Testing**: Cypress for end-to-end testing

## 📊 Test Coverage

### Backend Test Coverage: **90%+**
- **Unit Tests**: 200+ tests covering all services and utilities
- **Integration Tests**: API endpoint testing with database integration
- **Performance Tests**: Load testing, memory monitoring, response time validation
- **Security Tests**: Authentication, authorization, and input validation

### Frontend Test Coverage: **95%+**
- **Component Tests**: React component testing with user interactions
- **Store Tests**: Zustand state management testing
- **Service Tests**: API service layer testing with mocking
- **E2E Tests**: Complete user flow testing with Cypress

## 🛠️ Installation

### Prerequisites
- Python 3.11+ (3.13, 3.12, 3.11 supported)
- Node.js 18+
- PostgreSQL 13+
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-chat-app
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb ai_chat_app
   
   # Run migrations
   alembic upgrade head
   ```

5. **Run backend tests**
   ```bash
   pytest --cov=app --cov-report=html
   ```

6. **Start backend server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend-react
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your backend API URL
   ```

3. **Run frontend tests**
   ```bash
   npm test
   npm run test:coverage
   ```

4. **Start development server**
   ```bash
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
pytest tests/test_endpoints_comprehensive.py

# Run load tests
pytest tests/test_performance.py::TestLoadTesting
```

### Frontend Testing
```bash
# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run cypress:open
npm run cypress:run

# Run specific test suites
npm test -- --testPathPattern=HeaderBar
npm test -- --testPathPattern=auth
```

### E2E Testing
```bash
# Open Cypress
npx cypress open

# Run all E2E tests
npx cypress run

# Run specific test files
npx cypress run --spec "cypress/e2e/auth.cy.ts"
npx cypress run --spec "cypress/e2e/chat.cy.ts"
```

## 📈 Performance

### Backend Performance Metrics
- **Response Time**: < 100ms for health checks, < 500ms for API calls
- **Concurrent Users**: Supports 100+ concurrent connections
- **Memory Usage**: < 50MB increase under load
- **Database Queries**: Optimized with connection pooling
- **File Upload**: Handles 1MB+ files efficiently

### Frontend Performance Metrics
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
DATABASE_URL=postgresql://user:password@localhost/ai_chat_app

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
LITELLM_API_KEY=your-litellm-key
OPENAI_API_KEY=your-openai-key

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
serve -s build -l 3000
```

## 📚 API Documentation

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/chat/messages` - Send chat message
- `GET /api/v1/conversations/` - List conversations
- `POST /api/v1/knowledge/upload` - Upload documents
- `POST /api/v1/search` - Semantic search
- `GET /health` - Health check

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
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
- Check the documentation
- Review the troubleshooting section
- Contact the development team

---

**Built with ❤️ by the AI Chat Team**

## 🏢 Enterprise User Management

- **SSO (Single Sign-On)**: Unterstützt Google, Microsoft, GitHub, SAML, OIDC mit dynamischer Provider-Anzeige
- **Account-Linking**: Verknüpfung von SSO-Konten mit lokalen Accounts
- **JIT-Provisionierung**: Automatisches Anlegen von Usern bei erstem SSO-Login
- **Erweiterte RBAC**: Hierarchische Rollen (Super Admin, Admin, Manager, User, Guest), Gruppen, Bereichs-Admins
- **Feingranulare Rechte**: Rechteverwaltung auf Ressourcenebene
- **2FA/MFA**: Zwei-Faktor-Authentifizierung für erhöhte Sicherheit
- **Self-Service-UI**: User können API-Token, 2FA, Account-Löschung selbst verwalten
- **Audit-Log-API und UI**: Vollständiges Logging aller sicherheitsrelevanten Events
- **Bulk-Import/-Export**: Massenverwaltung von Usern und Rollen
- **DSGVO-Features**: Datenexport, Account-Löschung, Datenschutz-Compliance