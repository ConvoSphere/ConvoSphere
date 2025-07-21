# Frontend Architecture

## Overview

The new frontend of the AI Assistant Platform is implemented in `frontend-react/` and is based on **React** (TypeScript), **Ant Design** (UI), **Zustand** (state management), **i18next** (internationalization), **Axios** (API), and **Vite** (build tool). It is modular, responsive, and future-proof.

### Key Features
- Modern, modular React architecture
- Ant Design UI with light/dark mode and responsive sidebar
- State management with Zustand
- Internationalization (i18n) with i18next (EN/DE)
- Routing with React Router v6, protected routes
- WebSocket-based chat
- API integration with Axios
- Full backend integration for all core features (Chat, Knowledge Base, Tools, Assistants, Conversations, MCP Tools)
- Comprehensive tests with Jest & React Testing Library
- Accessibility (WCAG compliant)

## Technology Stack
- **React (TypeScript)**: UI framework
- **Ant Design**: UI components and design system
- **Zustand**: State management
- **i18next**: Internationalization
- **Axios**: API requests
- **Vite**: Build tool
- **Jest, React Testing Library**: Testing

## Project Structure

```
frontend-react/
├── src/
│   ├── components/      # Reusable UI components (Sidebar, Header, ThemeSwitcher, ...)
│   ├── pages/           # Pages (Chat, Dashboard, Knowledge Base, Tools, ...)
│   ├── services/        # API and WebSocket services
│   ├── store/           # Global state (Theme, Auth, ...)
│   ├── i18n/            # Translations and i18n initialization
│   ├── styles/          # Theme configuration
│   └── ...
├── public/
├── package.json
└── ...
```

## Main Features
- **Chat**: WebSocket-based real-time chat, default start page
- **Knowledge Base**: Document management, upload, search
- **Tools**: Tool list, execution, parameter input
- **Assistants**: AI assistant management
- **Conversations**: Overview and details of past conversations
- **MCP Tools**: Integration and execution of external tools
- **Settings, Admin, Profile**: Settings, user and system management

## Architectural Principles
- **Modularity**: Feature- and component-based
- **Maintainability**: Clear separation of UI, state, and services
- **Testability**: High test coverage, service mocking
- **Accessibility**: WCAG-compliant UI
- **Responsiveness**: Sidebar, header, and layout adapt to device

## Testing
- Component and service tests with Jest & React Testing Library
- API services are mocked
- Target test coverage >80%

## Migration
- Previous NiceGUI/Streamlit frontend has been fully removed
- All features and pages are now implemented as React components in `frontend-react/`
- No more code in src/ or frontend/ directories
- Parallel development and stepwise migration completed 