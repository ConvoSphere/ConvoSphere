# Architecture Overview

## System Architecture

The AI Assistant Platform follows a **modular, scalable architecture** designed for enterprise deployment. The system is built using modern technologies and best practices to ensure reliability, performance, and maintainability.

### Architecture Principles

1. **Separation of Concerns**: Clear separation between frontend, backend, and data layers
2. **Microservices Ready**: Modular design that can be decomposed into microservices
3. **Scalability First**: Horizontal scaling capabilities from the ground up
4. **Security by Design**: Security considerations integrated at every layer
5. **Performance Optimized**: Caching, connection pooling, and efficient data access patterns

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Client Layer                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Web Browser  │  Mobile App  │  Desktop App  │  API Clients  │  Admin UI   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Backend Layer                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  FastAPI REST API  │  WebSocket  │  Auth  │  Business Logic  │  Services    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Data Layer                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Redis Cache  │  Weaviate Vector DB  │  File Storage  │      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           External Services                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  AI Providers  │  MCP Tools  │  Monitoring  │  Backup Services  │  CDN      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Layer (React)

The frontend is built using **React (TypeScript)** with **Ant Design** for UI, **Zustand** for state management, and **i18next** for internationalization. It is fully decoupled from the backend and communicates via REST API and WebSocket.

#### Key Features
- Modular, feature-based structure
- Responsive sidebar and header
- Protected routes and authentication
- WebSocket-based chat as the default landing page
- Full backend integration for all core features (Chat, Knowledge Base, Tools, Assistants, Conversations, MCP Tools)
- Comprehensive component and service tests (Jest, React Testing Library)
- Accessibility (WCAG) and dark mode support
- Internationalization (EN/DE, easily extendable)

#### Frontend Structure
```
frontend-react/
├── src/
│   ├── components/      # Reusable UI components (Sidebar, Header, ThemeSwitcher, ...)
│   ├── pages/           # Pages (Chat, Dashboard, Knowledge Base, Tools, ...)
│   ├── services/        # API and WebSocket services
│   ├── store/           # Global state (Theme, Auth, ...)
│   ├── i18n/            # Translations and i18n setup
│   ├── styles/          # Theme configuration
│   └── ...
├── public/
├── package.json
└── ...
```

### Backend Layer (FastAPI)

The backend is built using **FastAPI**, a modern, high-performance web framework for building APIs with Python. It provides REST endpoints, WebSocket communication, authentication, business logic, and integration with external services.

#### Backend Structure
```
backend/
├── app/
│   ├── api/             # REST API endpoints
│   ├── core/            # Configuration, security, database
│   ├── models/          # Database models
│   ├── services/        # Business logic and integrations
│   ├── tools/           # MCP tool implementations
│   └── ...
├── migrations/
├── requirements.txt
└── ...
```

### Data Layer
- **PostgreSQL**: Primary database for user data, conversations, and metadata
- **Redis**: Caching, session management, and real-time features
- **Weaviate**: Vector database for semantic search and embeddings
- **File Storage**: Document uploads and static assets

### External Integrations
- **AI Providers**: OpenAI, Anthropic, and other LLM providers
- **MCP Tools**: Model Context Protocol for tool integration
- **Monitoring**: Health checks, logging, and metrics
- **CDN**: Static asset delivery

## Accessibility & Internationalization
- All UI components are designed for accessibility (WCAG 2.1 AA)
- Keyboard navigation and screen reader support
- Light/dark mode with high-contrast color palettes
- Internationalization with i18next (English, German, easily extendable)

## Testing & Quality
- Component and service tests with Jest & React Testing Library
- API services are fully mockable for frontend tests
- Test coverage >80% targeted for all core features

## Migration Note
- The legacy NiceGUI/Streamlit frontend has been fully replaced by the new React architecture.
- All features and pages have been re-implemented as React components.
- Parallel development and incremental migration were supported during the transition. 