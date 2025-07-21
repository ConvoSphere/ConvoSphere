# ConvoSphere React Frontend

Dieses Frontend basiert auf React, Vite, TypeScript, Ant Design, Zustand, i18next und ist für eine moderne, skalierbare AI-Plattform ausgelegt.

## Features
- Ant Design UI mit Light/Dark Mode
- State-Management mit Zustand
- Internationalisierung (i18n) mit englisch und deutsch
- Routing mit React Router
- API-Service mit Axios
- WebSocket-Chat
- Backend-Anbindung für Knowledge Base, Tools, Assistants, Conversations, MCP Tools
- Beispiel-Tests mit React Testing Library & Jest
- Barrierefreiheit und Theme-Switcher

## Setup

```bash
cd frontend-react
npm install
npm run dev
```

## Projektstruktur
- `src/components/` – Wiederverwendbare UI-Komponenten (ThemeSwitcher, Sidebar, Header, ...)
- `src/pages/` – Seiten (Chat, Dashboard, Knowledge Base, Tools, ...)
- `src/services/` – API- und WebSocket-Services
- `src/store/` – Globaler Zustand (Theme, Auth, ...)
- `src/i18n/` – Übersetzungen und i18n-Initialisierung
- `src/styles/` – Theme-Konfiguration

## Testen

```bash
npm run test
```
- Tests für Komponenten und Services mit Jest & React Testing Library
- API-Services werden gemockt
- Beispiel: `src/pages/Chat.test.tsx`, `src/services/tools.test.ts`, ...

## Entwicklung
- Alle Kernfeatures sind modular und mit dem Backend verbunden
- Error- und Loading-Handling integriert
- Responsive Sidebar und Header
- Barrierefreiheit und Theme-Switcher

## Backend-Anbindung
- Die wichtigsten Features (Chat, Knowledge Base, Tools, Assistants, Conversations, MCP Tools) sind mit den jeweiligen API-Endpunkten verbunden
- Anpassungen an die Backend-API können in den Services vorgenommen werden

## Nächste Schritte
- Features und Seiten weiter ausbauen
- UI/UX-Feinschliff, Error Handling, Loading States
- Weitere Tests und Dokumentation