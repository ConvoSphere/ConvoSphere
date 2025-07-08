# Frontend (React) – Overview

> **Status:** _✅ Complete – last updated 2025-01-XX_

The legacy Streamlit UI has been **replaced** by a modern React 18 + Vite + TypeScript application that embraces ConvoSphere's brand values of _zugängliche, klare und empathische Kommunikation_.

---

## 1 Goals

* ✅ Rich, responsive SPA that consumes the FastAPI backend (`/docs`)
* ✅ Clean component structure with Redux Toolkit state‐management and React Router
* ✅ JWT authentication (registration & login) with guarded routes
* ✅ Full Tailwind CSS design system implementing the ConvoSphere Brandbook
* ✅ Accessibility (WCAG AA+), i18n and light/dark theme toggle
* 🚧 Robust test-suite (Jest + RTL, Cypress E2E) - In Progress
* ✅ Docker-first dev/prod deployment alongside the backend

## 2 Tech-Stack

| Layer | Library / Tool | Purpose |
|-------|----------------|---------|
| Build | **Vite** + TypeScript | Fast dev-server & optimized production build |
| UI | **React 18**, **Tailwind CSS** | Component rendering & styling |
| State | **Redux Toolkit**, **React-Redux**, **@reduxjs/toolkit/query** | Global state & API cache |
| Data-fetch | **RTK Query** | HTTP client with JWT interceptor & caching |
| Routing | **React Router v6.22** | SPA navigation |
| Tests | **Jest**, **React Testing Library**, **Cypress** | Unit / integration / E2E |
| Lint/Format | **ESLint**, **Prettier**, **Husky + lint-staged** | Code quality & pre-commit hooks |

## 3 Project Layout

```
frontend/
├── public/           # static assets, favicons, index.html
├── src/
│   ├── app/          # Redux store configuration
│   ├── components/   # reusable UI primitives
│   │   ├── ui/       # Button, Input, Card, ThemeToggle, FileUpload
│   │   ├── ErrorBoundary.tsx
│   │   └── ProtectedRoute.tsx
│   ├── features/     # vertical slices (auth, chat, dashboard …)
│   │   └── auth/
│   │       └── authSlice.ts
│   ├── hooks.ts      # custom React hooks
│   ├── pages/        # route components
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   └── Chat.tsx
│   ├── router/       # React-Router configuration
│   ├── services/     # API and external services
│   │   ├── apiSlice.ts
│   │   ├── authService.ts
│   │   ├── websocketService.ts
│   │   └── fileService.ts
│   ├── styles/       # Tailwind config extensions & global.css
│   └── main.tsx      # app entry point
├── tailwind.config.ts
├── tsconfig.json
└── vite.config.ts
```

## 4 Branding & Theme System

Tailwind is extended with the ConvoSphere palette:

```ts title="tailwind.config.ts"{4-11}
export default {
  theme: {
    extend: {
      colors: {
        indigo: {
          DEFAULT: '#23224A', // Deep Indigo
        },
        azure: '#5BC6E8',     // Soft Azure
        sand: '#F5E9DD',      // Warm Sand
        lime: '#B6E74B',      // Accent Lime
        slate: '#7A869A',     // Slate Grey
        smoke: '#F7F9FB',    // White Smoke
      },
    },
  },
  darkMode: 'class',
};
```

Light/dark mode is toggled via `class="dark"` on `<html>` and persisted in `localStorage`.

## 5 Authentication Flow

1. ✅ User registers / logs in -> `/auth/register`, `/auth/login` routes.
2. ✅ Backend returns **JWT access & refresh** tokens.
3. ✅ Tokens stored in `localStorage` and injected into RTK Query `Authorization` header.
4. ✅ RTK Query 401 responses trigger silent refresh; failure redirects to login.

See [`docs/frontend/auth.md`](auth.md) for details.

## 6 Running Locally

```
# terminal 1 – backend
$ docker compose up backend

# terminal 2 – frontend dev-server
$ cd frontend
$ npm install
$ npm run dev       # Vite on http://localhost:5173
```

Docker Compose adds a `frontend` service for production builds; see [`docs/frontend/docker.md`](docker.md).

## 7 Testing

```
# unit & integration
$ npm test

# cypress E2E (interactive)
$ npm run cypress open
```

## 8 Migration Guide

Old Streamlit artifacts are archived under `docs/legacy/frontend-streamlit.md`. All new contributions must follow this React architecture.

## 9 Implemented Features

### ✅ **Core Features**
- **Authentication System**: JWT with refresh token logic
- **Dashboard**: Statistics and recent activity
- **Chat Interface**: Real-time messaging with WebSockets
- **File Upload**: Progress tracking and validation
- **Error Handling**: Error boundaries and graceful degradation
- **Theme System**: Light/dark mode toggle
- **Protected Routes**: Authentication guards

### ✅ **API Integration**
- **RTK Query**: Comprehensive API layer with caching
- **WebSocket Service**: Real-time chat communication
- **File Service**: Upload and management
- **Auth Service**: Token management and session handling

### ✅ **UI Components**
- **Button**: Multiple variants and states
- **Input**: Form inputs with validation
- **Card**: Content containers
- **ThemeToggle**: Dark/light mode switch
- **FileUpload**: Drag-and-drop file upload
- **ErrorBoundary**: Graceful error handling

### 🚧 **In Progress**
- **Testing**: Unit and integration tests
- **Assistant Management**: UI for managing AI assistants
- **Knowledge Base**: Document management interface
- **Advanced Chat**: Message search, export, context management

## 10 API Endpoints

The frontend integrates with the following backend endpoints:

- ✅ `/api/v1/auth/login` - User authentication
- ✅ `/api/v1/auth/register` - User registration
- ✅ `/api/v1/auth/me` - Current user info
- ✅ `/api/v1/auth/refresh` - Token refresh
- ✅ `/api/v1/conversations/` - Conversation management
- ✅ `/api/v1/dashboard/stats` - Dashboard statistics
- ✅ `/api/v1/dashboard/overview` - Dashboard overview
- ✅ `/api/v1/chat/ws/{conversation_id}` - WebSocket chat

## 11 Development Status

**Overall Progress: 90% Complete**

- **Core Features**: 100% ✅
- **API Integration**: 100% ✅
- **UI Components**: 100% ✅
- **Authentication**: 100% ✅
- **Real-time Features**: 100% ✅
- **Testing**: 20% 🚧
- **Advanced Features**: 30% 🚧
