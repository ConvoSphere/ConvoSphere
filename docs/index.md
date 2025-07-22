# AI Chat Application

A modern, full-stack AI chat application built with **FastAPI** (Backend) and **React** (Frontend), featuring comprehensive test coverage, real-time messaging, and advanced AI capabilities.

<div class="grid cards" markdown>

-   :fontawesome-solid-rocket: __[Quick Start](getting-started/quick-start.md)__
    
    Get up and running in under 10 minutes with our step-by-step guide.

-   :fontawesome-solid-book: __[User Guide](user-guide/getting-started.md)__
    
    Learn how to use the chat interface, manage files, and customize settings.

-   :fontawesome-solid-code: __[API Reference](api/overview.md)__
    
    Complete API documentation with examples and interactive testing.

-   :fontawesome-solid-cogs: __[Architecture](architecture/overview.md)__
    
    Understand the system design, components, and data flow.

</div>

## 🚀 Key Features

### Core Capabilities

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

## 🏗️ Architecture Overview

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

## 📊 System Performance

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

## 🧪 Test Coverage

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

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **PostgreSQL**: Primary database for user data and conversations
- **Redis**: Caching and session storage
- **Weaviate**: Vector database for semantic search
- **LiteLLM**: AI provider abstraction layer

### Frontend
- **React 18**: Modern React with concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Zustand**: Lightweight state management
- **Ant Design**: Enterprise UI component library
- **WebSocket**: Real-time communication
- **React Router**: Client-side routing

### Development & Testing
- **Python 3.11+**: Backend programming language
- **Node.js 18+**: Frontend runtime
- **Pytest**: Python testing framework
- **Jest**: JavaScript testing framework
- **Cypress**: End-to-end testing
- **Docker**: Containerization and deployment

## 🚀 Quick Start

Get up and running in under 10 minutes:

```bash
# Clone the repository
git clone https://github.com/your-org/ai-chat-app.git
cd ai-chat-app

# Quick setup with Docker
docker-compose up --build

# Or manual setup
make setup
make install
make dev
```

**Ready to dive deeper?** Check out our [Quick Start Guide](getting-started/quick-start.md) for detailed instructions.

## 📚 Documentation Sections

### Getting Started
- **[Quick Start](getting-started/quick-start.md)** - Get up and running in minutes
- **[Installation](getting-started/installation.md)** - Detailed installation instructions
- **[Configuration](getting-started/configuration.md)** - Environment and service setup
- **[First Steps](getting-started/first-steps.md)** - Your first conversation

### Architecture
- **[Overview](architecture/overview.md)** - High-level system architecture
- **[System Design](architecture/system-design.md)** - Detailed system design patterns
- **[Backend](architecture/backend.md)** - FastAPI backend architecture
- **[Frontend](architecture/frontend.md)** - React frontend architecture
- **[Database](architecture/database.md)** - Database design and schema
- **[Security](architecture/security.md)** - Security architecture and best practices

### Development
- **[Setup](development/setup.md)** - Development environment setup
- **[Testing](development/testing.md)** - Running tests and test coverage
- **[Contributing](development/contributing.md)** - How to contribute to the project
- **[Code Style](development/code-style.md)** - Coding standards and conventions
- **[API Development](development/api-development.md)** - API development guidelines

### API Reference
- **[Overview](api/overview.md)** - API design principles and patterns
- **[Authentication](api/authentication.md)** - Authentication and authorization
- **[Users](api/users.md)** - User management endpoints
- **[Chat](api/chat.md)** - Chat and messaging endpoints
- **[Conversations](api/conversations.md)** - Conversation management
- **[Knowledge Base](api/knowledge.md)** - Document and knowledge management
- **[Tools](api/tools.md)** - Tool integration endpoints
- **[WebSocket](api/websocket.md)** - Real-time communication
- **[Errors](api/errors.md)** - Error handling and codes

### Features
- **[AI Integration](features/ai-integration.md)** - AI provider integration details
- **[Real-time Chat](features/real-time-chat.md)** - WebSocket-based messaging
- **[Knowledge Base](features/knowledge-base.md)** - Document processing and search
- **[File Upload](features/file-upload.md)** - File handling and processing
- **[User Management](features/user-management.md)** - User and role management
- **[Security](features/security.md)** - Security features and best practices
- **[Performance](features/performance.md)** - Performance optimization

### Deployment
- **[Docker](deployment/docker.md)** - Containerized deployment
- **[Production](deployment/production.md)** - Production deployment guide
- **[Monitoring](deployment/monitoring.md)** - Monitoring and observability
- **[CI/CD](deployment/ci-cd.md)** - Continuous integration and deployment

### User Guide
- **[Getting Started](user-guide/getting-started.md)** - User onboarding guide
- **[Chat Interface](user-guide/chat-interface.md)** - Using the chat interface
- **[File Management](user-guide/file-management.md)** - Managing uploaded files
- **[Settings](user-guide/settings.md)** - User preferences and settings
- **[Troubleshooting](user-guide/troubleshooting.md)** - Common issues and solutions

### Project
- **[Status](project/status.md)** - Current implementation status and progress
- **[Roadmap](project/roadmap.md)** - Development roadmap and timeline
- **[Changelog](project/changelog.md)** - Version history and changes
- **[Contributing](project/contributing.md)** - How to contribute

## 🔒 Security Features

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

## 🏢 Enterprise Features

### SSO (Single Sign-On)
- Support for OIDC, SAML, OAuth2 (Google, Microsoft, GitHub)
- SSO login, callback, and account linking
- Just-in-Time provisioning and SSO attribute mapping
- SSO configuration guide in deployment section

### Advanced RBAC
- Hierarchical roles (Super Admin, Admin, Manager, User, Guest)
- Group-based permissions and department admins
- Fine-grained permission management (e.g., resource-level)
- Admin UI for roles, permissions, and groups

### Security & Self-Service
- 2FA/MFA (TOTP, WebAuthn)
- Self-service UI for users (API tokens, 2FA, account deletion)
- Bulk import/export of users/roles
- GDPR features (data export, account deletion)

### Audit Logging
- Audit log API and UI for admins
- Logging of all security-relevant events (login, SSO, role changes)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details on:

- Setting up your development environment
- Code style and conventions
- Testing requirements
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

- **Documentation**: This site contains comprehensive documentation
- **Issues**: Report bugs and request features on [GitHub](https://github.com/your-org/ai-chat-app/issues)
- **Discussions**: Join our [Discord server](https://discord.gg/your-server) for community support

---

<div align="center">

**Ready to get started?** [Quick Start Guide →](getting-started/quick-start.md)

**Want to see the current status?** [Project Status →](project/status.md)

</div> 