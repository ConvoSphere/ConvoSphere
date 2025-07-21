# ConvoSphere React Frontend

This frontend is based on React, Vite, TypeScript, Ant Design, Zustand, and i18next, designed for a modern, scalable AI platform.

## Features
- Ant Design UI with Light/Dark Mode
- State management with Zustand
- Internationalization (i18n) with English and German
- Routing with React Router (v6)
- API service with Axios
- WebSocket chat
- Backend integration for Knowledge Base, Tools, Assistants, Conversations, MCP Tools
- Example tests with React Testing Library & Jest
- Accessibility and theme switcher

## Setup

```bash
cd frontend-react
npm install
npm run dev
```

## Project Structure
- `frontend-react/src/components/` – Reusable UI components (ThemeSwitcher, Sidebar, Header, ...)
- `frontend-react/src/pages/` – Pages (Chat, Dashboard, Knowledge Base, Tools, ...)
- `frontend-react/src/services/` – API and WebSocket services
- `frontend-react/src/store/` – Global state (Theme, Auth, ...)
- `frontend-react/src/i18n/` – Translations and i18n initialization
- `frontend-react/src/styles/` – Theme configuration

## Testing

```bash
npm run test
```
- Component and service tests with Jest & React Testing Library
- API services are mocked
- Example: `frontend-react/src/pages/Chat.test.tsx`, `frontend-react/src/services/tools.test.ts`, ...

## Development
- All core features are modular and connected to the backend
- Error and loading handling integrated
- Responsive sidebar and header
- Accessibility and theme switcher

## Backend Integration
- All main features (Chat, Knowledge Base, Tools, Assistants, Conversations, MCP Tools) are connected to their respective API endpoints
- Backend API adjustments can be made in the services

## Next Steps
- Expand features and pages
- UI/UX polish, error handling, loading states
- More tests and documentation

## Admin CLI

The central CLI tool for admin and maintenance tasks is located at `backend/cli.py` and can be used directly (thanks to the shebang):

```bash
./backend/cli.py [COMMAND] [SUBCOMMAND] [OPTIONS]
```

### Examples
- Database migration: `./backend/cli.py db migrate`
- Create admin user: `./backend/cli.py user create-admin`
- List users: `./backend/cli.py user list`
- Health check: `./backend/cli.py health check`
- Validate translations: `./backend/cli.py translations validate`
- Start example MCP server: `./backend/cli.py mcp start-server`
- Run API integration tests: `./backend/cli.py test api-integration`

**Note:**
All previous scripts from the `scripts/` folder have been migrated as CLI subcommands. Use the CLI for all administrative, testing, and utility tasks. This ensures a unified, maintainable, and extensible admin interface.