# Frontend Architecture

## Overview

Das neue Frontend der AI Assistant Platform basiert auf **React** (TypeScript), **Ant Design** (UI), **Zustand** (State-Management), **i18next** (Internationalisierung), **Axios** (API), **Vite** (Build-Tool) und ist modular, responsiv und zukunftssicher aufgebaut.

### Key Features
- Moderne, modulare React-Architektur
- Ant Design UI mit Light/Dark Mode und Responsive Sidebar
- State-Management mit Zustand
- Internationalisierung (i18n) mit i18next (DE/EN)
- Routing mit React Router, Protected Routes
- WebSocket-basierter Chat
- API-Integration mit Axios
- Vollständige Backend-Anbindung für alle Kernfeatures (Chat, Knowledge Base, Tools, Assistants, Conversations, MCP Tools)
- Umfassende Tests mit Jest & React Testing Library
- Barrierefreiheit (WCAG-konform)

## Technology Stack
- **React (TypeScript)**: UI-Framework
- **Ant Design**: UI-Komponenten und Design-System
- **Zustand**: State-Management
- **i18next**: Internationalisierung
- **Axios**: API-Requests
- **Vite**: Build-Tool
- **Jest, React Testing Library**: Testing

## Projektstruktur

```
frontend-react/
├── src/
│   ├── components/      # Wiederverwendbare UI-Komponenten (Sidebar, Header, ThemeSwitcher, ...)
│   ├── pages/           # Seiten (Chat, Dashboard, Knowledge Base, Tools, ...)
│   ├── services/        # API- und WebSocket-Services
│   ├── store/           # Globaler Zustand (Theme, Auth, ...)
│   ├── i18n/            # Übersetzungen und i18n-Initialisierung
│   ├── styles/          # Theme-Konfiguration
│   └── ...
├── public/
├── package.json
└── ...
```

## Hauptfeatures
- **Chat**: WebSocket-basierter Echtzeit-Chat, direkt als Startseite
- **Knowledge Base**: Dokumentenverwaltung, Upload, Suche
- **Tools**: Tool-Liste, Ausführung, Parameterübergabe
- **Assistants**: Verwaltung von AI-Assistants
- **Conversations**: Übersicht und Details vergangener Konversationen
- **MCP Tools**: Integration und Ausführung externer Tools
- **Settings, Admin, Profile**: Einstellungen, User- und Systemverwaltung

## Architekturprinzipien
- **Modularität**: Feature- und Komponenten-basiert
- **Wartbarkeit**: Klare Trennung von UI, State, Services
- **Testbarkeit**: Hohe Testabdeckung, Mocking von Services
- **Barrierefreiheit**: WCAG-konforme UI
- **Responsivität**: Sidebar, Header, Layout passen sich an

## Testing
- Komponenten- und Service-Tests mit Jest & React Testing Library
- API-Services werden gemockt
- Testabdeckung >80% angestrebt

## Migration
- NiceGUI/Streamlit wurde vollständig entfernt
- Alle Features und Seiten wurden als React-Komponenten neu umgesetzt
- Parallele Entwicklung und schrittweise Migration möglich 