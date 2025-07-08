# Frontend (React) – Overview

> **Status:** _Refactor in progress – last updated 2025-07-04_

The legacy Streamlit UI has been **replaced** by a modern React 18 + Vite + TypeScript application that embraces ConvoSphere’s brand values of _zugängliche, klare und empathische Kommunikation_.

---

## 1 Goals

* Rich, responsive SPA that consumes the FastAPI backend (`/docs`)
* Clean component structure with Redux Toolkit state‐management and React Router
* JWT authentication (registration & login) with guarded routes
* Full Tailwind CSS design system implementing the ConvoSphere Brandbook
* Accessibility (WCAG AA+), i18n and light/dark theme toggle
* Robust test-suite (Jest + RTL, Cypress E2E)
* Docker-first dev/prod deployment alongside the backend

## 2 Tech-Stack

| Layer | Library / Tool | Purpose |
|-------|----------------|---------|
| Build | **Vite** + TypeScript | Fast dev-server & optimized production build |
| UI | **React 18**, **Tailwind CSS** | Component rendering & styling |
| State | **Redux Toolkit**, **React-Redux**, **@reduxjs/toolkit/query** | Global state & API cache |
| Data-fetch | **Axios** | HTTP client with JWT interceptor |
| Routing | **React Router v6.22** | SPA navigation |
| Tests | **Jest**, **React Testing Library**, **Cypress** | Unit / integration / E2E |
| Lint/Format | **ESLint**, **Prettier**, **Husky + lint-staged** | Code quality & pre-commit hooks |

## 3 Project Layout

```
frontend/
├── public/           # static assets, favicons, index.html
├── src/
│   ├── api/          # Axios instances, RTK Query services
│   ├── app/          # Redux store configuration
│   ├── components/   # reusable UI primitives
│   ├── features/     # vertical slices (auth, chat, dashboard …)
│   ├── hooks/        # custom React hooks
│   ├── pages/        # route components
│   ├── router/       # React-Router wrappers
│   ├── styles/       # Tailwind config extensions & global.css
│   ├── utils/        # helpers, constants
│   └── index.tsx     # app entry point
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

1. User registers / logs in -> `/auth/register`, `/auth/login` routes.
2. Backend returns **JWT access & refresh** tokens.
3. Tokens stored in `localStorage` and injected into Axios `Authorization` header.
4. Axios 401 responses trigger silent refresh; failure redirects to login.

See [`docs/frontend/auth.md`](auth.md) for details.

## 6 Running Locally

```
# terminal 1 – backend
$ docker compose up backend

# terminal 2 – frontend dev-server
$ cd frontend
$ pnpm install   # or npm / yarn
$ pnpm dev       # Vite on http://localhost:5173
```

Docker Compose adds a `frontend` service for production builds; see [`docs/frontend/docker.md`](docker.md).

## 7 Testing

```
# unit & integration
$ pnpm test

# cypress E2E (interactive)
$ pnpm cypress open
```

## 8 Migration Guide

Old Streamlit artifacts are archived under `docs/legacy/frontend-streamlit.md`. All new contributions must follow this React architecture.
