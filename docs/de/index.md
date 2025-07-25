# ConvoSphere - AI Chat Platform

Eine moderne, umfassende AI-Chat-Anwendung mit **FastAPI** (Backend) und **React** (Frontend), die Echtzeit-Messaging, erweiterte Knowledge Base und AI-Funktionen auf Enterprise-Level bietet.

<div align="center">

![ConvoSphere](https://img.shields.io/badge/ConvoSphere-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

[![Documentation](https://img.shields.io/badge/Documentation-MkDocs-blue)](https://your-org.github.io/convosphere/)
[![Tests](https://img.shields.io/badge/Tests-Passing-green)](https://github.com/your-org/convosphere/actions)
[![Coverage](https://img.shields.io/badge/Coverage-95%25+-green)](https://github.com/your-org/convosphere/actions)

</div>

## 🚀 Quick Start (5 Minuten)

**ConvoSphere in unter 5 Minuten einsatzbereit:**

```bash
# Repository klonen
git clone https://github.com/your-org/convosphere.git
cd convosphere

# Mit Docker starten (empfohlen)
docker-compose up --build

# Oder manuelles Setup
make setup
make install
make dev
```

→ [http://localhost:5173](http://localhost:5173) öffnen (Frontend) | [http://localhost:8000](http://localhost:8000) (Backend API)

**Erste Schritte:**
1. Registrieren Sie sich oder melden Sie sich an
2. Starten Sie eine Konversation mit AI-Assistenten
3. Laden Sie Dokumente in die Knowledge Base hoch
4. Erstellen Sie benutzerdefinierte AI-Assistenten
5. Erkunden Sie Tools und Integrationen

## 📖 Für Benutzer

- **[User Guide](user-guide.md)** - Vollständige Anleitung für ConvoSphere
- **[FAQ](faq.md)** - Häufige Fragen und Lösungen
- **[Quick Start](quick-start.md)** - In 5 Minuten startklar

## 🔧 Für Entwickler

- **[Developer Guide](developer-guide.md)** - Setup, Architektur, Entwicklung
- **[API Reference](../api.md)** - Vollständige API-Dokumentation
- **[Features Documentation](../features/)** - Detaillierte Feature-Spezifikationen
- **[Architecture Guide](../architecture.md)** - Systemdesign und Komponenten

## ✨ Aktuelles Feature-Set

### 💬 **Echtzeit-Chat & Messaging** ✅
- **WebSocket-basierte Konversationen** mit sofortiger Zustellung
- **Datei-Anhänge** (PDF, DOCX, TXT, MD) bis zu 50MB
- **Audio-Datei-Verarbeitung** mit automatischer Spracherkennung (ASR)
- **Schreibindikatoren** und Echtzeit-Status
- **Konversations-Management** mit Verlauf und Suche
- **Rich-Text-Anzeige** mit ordnungsgemäßer Formatierung

### 📚 **Erweiterte Knowledge Base** ✅
- **Dokumenten-Upload** mit Drag & Drop und Bulk-Import
- **Semantische Suche** mit AI-gestützter Content-Erkennung
- **Tag-Management** mit Tag-Clouds und Statistiken
- **Rollenbasierte Zugriffskontrolle** (User/Premium/Moderator/Admin)
- **Dokumentenverarbeitung** mit automatischer Textextraktion und Chunking
- **Erweiterte Filterung** nach Metadaten, Tags und Inhalten
- **Performance-Optimierungen** mit Virtualisierung und Caching
- **Chat-Integration** für kontextbezogene AI-Antworten
- **Audio-Datei-Transkription** (MP3, WAV) mit durchsuchbarem Inhalt

### 🤖 **AI-Integration & Assistenten** ✅
- **Multiple AI-Provider** (OpenAI, Anthropic, etc.) über LiteLLM
- **Benutzerdefinierte AI-Assistenten** mit konfigurierbaren Persönlichkeiten
- **Kontextbezogene Antworten** unter Verwendung der Knowledge Base
- **Tool-Ausführung** und Model Context Protocol (MCP) Integration
- **Assistenten-Management** mit Templates und Sharing
- **AI-Modell-Auswahl** und Parameter-Tuning

### 🔧 **Tools & Integrationen** ✅
- **MCP (Model Context Protocol)** Tool-Integration
- **Benutzerdefinierte Tool-Entwicklung** und Management
- **Tool-Ausführungs-Tracking** mit Performance-Metriken
- **Externe API-Integrationen** und Webhooks
- **Such-Tools** und Rechner-Funktionen
- **Dateiverarbeitungs-Tools** und Utilities

### 👥 **Benutzerverwaltung & Administration** ✅
- **JWT-basierte Authentifizierung** mit Refresh-Tokens
- **Umfassende SSO-Integration** (LDAP, SAML, OAuth2, Google, Microsoft, GitHub)
- **Rollenbasierte Zugriffskontrolle** mit 4 Benutzerebenen
- **Benutzerregistrierung** und Profilverwaltung
- **Erweiterte Admin-Dashboard** mit Systemüberblick
- **Benutzer-Analytics** und Aktivitäts-Tracking
- **Umfassendes Audit-Logging** und Sicherheits-Monitoring
- **SSO-Account-Verknüpfung** und Benutzer-Bereitstellung
- **Bulk-Benutzer-Synchronisation** von SSO-Providern

### 🎨 **Benutzererfahrung & Interface** ✅
- **Modernes React 18** Frontend mit TypeScript
- **Responsive Design** optimiert für Mobile, Tablet und Desktop
- **Dark/Light Theme** Switching mit System-Präferenz-Erkennung
- **Internationalisierung** (Englisch/Deutsch) mit i18next
- **Error Boundaries** und umfassendes Error Handling
- **Lazy Loading** und Code Splitting für optimale Performance

### 📊 **Erweiterte Performance & Monitoring** ✅ ⭐
**Hinweis: Dieses Feature ist umfassender als typische Implementierungen**
- **Echtzeit-Performance-Tracking** mit Web Vitals (FCP, LCP, FID, CLS)
- **Speicher-Monitoring** mit JavaScript Heap-Analyse
- **Navigation-Timing-Analyse** mit detaillierten Metriken
- **Error-Tracking** und automatisierte Berichterstattung
- **Cache-Performance-Monitoring** mit Hit-Raten und Optimierung
- **Netzwerk-Status-Monitoring** und Offline-Erkennung
- **Performance-Visualisierung** mit Charts und Echtzeit-Dashboards
- **System-Health-Monitoring** mit Server-Metriken
- **Datenbank-Performance** Tracking

### 🔄 **Intelligentes Caching-System** ✅ ⭐
**Hinweis: Erweiterte Caching-Implementierung mit intelligentem Management**
- **Multi-Level-Caching** mit Größen- und TTL-Management
- **LRU-Eviction** mit Zugriffshäufigkeits-Tracking
- **Automatisches Cache-Warming** für häufig zugerufene Daten
- **Cache-Hit-Rate-Optimierung** mit Performance-Analytics
- **Memory-Management** mit konfigurierbaren Limits
- **Cache-Statistiken** und Monitoring-Dashboard

## 🚧 **Geplante Features** (In Entwicklung)

### 🎤 **Voice & Speech Features** (Geplant)
- **Spracheingabe** mit Speech-to-Text-Funktionalität *(UI bereit, Implementierung ausstehend)*
- **Sprachnachrichten-Aufnahme** und Wiedergabe
- **Mehrsprachige Spracherkennung**

### 📤 **Erweiterte Export & Sharing** (Geplant)
- **Konversations-Export** zu PDF, JSON und anderen Formaten *(UI bereit, Backend ausstehend)*
- **Konversations-Sharing** mit anderen Benutzern *(UI bereit, Implementierung ausstehend)*
- **Bulk-Konversations-Management** und Archivierung

### ✨ **Rich Text & Formatierung** (Geplant)
- **Markdown-Nachrichten-Formatierung** mit Live-Vorschau *(Placeholder-Tests vorhanden)*
- **Rich-Text-Editor** mit Formatierungs-Toolbar
- **Code-Syntax-Highlighting** in Nachrichten
- **Tabellen- und Listen-Formatierung** Support

### 🔐 **Erweiterte Sicherheit** (Geplant)
- **Zwei-Faktor-Authentifizierung (2FA)** mit Authenticator-Apps
- **Multi-Faktor-Authentifizierung (MFA)** Optionen
- **Erweiterte Session-Management** mit Geräte-Tracking
- **Sicherheits-Audit-Dashboard** mit Bedrohungs-Erkennung

### 📱 **Offline & Mobile** (Geplant)
- **Echte Offline-Funktionalität** mit Service Workern *(aktuell: nur intelligentes Caching)*
- **Progressive Web App (PWA)** Features
- **Mobile App** für iOS und Android
- **Offline-Dokumenten-Verarbeitung** und Synchronisation

### 🧠 **Erweiterte AI-Features** (Geplant)
- **Conversation Intelligence** mit Sentiment-Analyse
- **Intelligente Konversations-Zusammenfassung**
- **AI-gestützte Content-Empfehlungen**
- **Multi-modale AI** Integration (Text, Bild, Audio)

## 🏗️ Architektur

ConvoSphere folgt einer modernen, skalierbaren Architektur mit klarer Trennung der Belange:

```mermaid
graph TB
    subgraph "Frontend (React 18 + TypeScript)"
        UI[React UI Komponenten]
        WS[WebSocket Client]
        State[Zustand State Management]
        Router[React Router]
        Lazy[Lazy Loading]
        Cache[Intelligenter Cache Manager]
        Perf[Performance Monitor]
    end
    
    subgraph "Backend (FastAPI)"
        API[REST API]
        WS_Server[WebSocket Server]
        Auth[JWT Authentication]
        SSO[Umfassendes SSO]
        AI[AI Services]
        KB[Knowledge Base]
        Tools[MCP Tools]
        Admin[Admin Services]
        ASR[Audio-Spracherkennung]
    end
    
    subgraph "Daten-Layer"
        PG[(PostgreSQL<br/>Haupt-Datenbank)]
        Redis[(Redis<br/>Cache & Sessions)]
        Weaviate[(Weaviate<br/>Vector-Datenbank)]
        Storage[(File Storage)]
    end
    
    subgraph "Externe Services"
        AI_Providers[AI Provider<br/>OpenAI, Anthropic, etc.]
        SSO_Providers[SSO Provider<br/>LDAP, SAML, OAuth2]
        MCP_Tools[MCP Tools<br/>Externe Tools]
        Monitor[Monitoring<br/>Performance & Health]
    end
    
    UI --> API
    UI --> WS_Server
    State --> UI
    Router --> UI
    Lazy --> UI
    Cache --> UI
    Perf --> UI
    
    API --> Auth
    API --> SSO
    API --> AI
    API --> KB
    API --> Tools
    API --> Admin
    API --> ASR
    WS_Server --> Auth
    
    Auth --> PG
    SSO --> SSO_Providers
    AI --> AI_Providers
    AI --> Redis
    KB --> Weaviate
    KB --> Storage
    Tools --> MCP_Tools
    Admin --> PG
    Admin --> Monitor
    ASR --> Storage
    
    API --> PG
    API --> Redis
```

## 🛠️ Vollständiger Technologie-Stack

### **Frontend Stack**
- **React 18** mit TypeScript und Concurrent Features
- **Ant Design** Enterprise UI-Komponenten-Bibliothek
- **Zustand** leichtgewichtiges State Management
- **React Router** mit geschützten Routen
- **WebSocket** Client für Echtzeit-Kommunikation
- **i18next** für Internationalisierung (EN/DE)
- **Vite** für schnelle Entwicklung und optimierte Builds
- **Custom Performance Monitor** mit Web Vitals
- **Intelligenter Cache Manager** mit LRU-Eviction

### **Backend Stack**
- **FastAPI** modernes, schnelles Web-Framework mit Auto-Dokumentation
- **SQLAlchemy** ORM mit PostgreSQL
- **Redis** für Caching und Session-Storage
- **Weaviate** Vector-Datenbank für semantische Suche
- **LiteLLM** AI-Provider-Abstraktions-Layer
- **JWT** Authentifizierung mit Refresh-Tokens
- **WebSocket** für Echtzeit-Messaging
- **Umfassendes SSO** (LDAP, SAML, OAuth2)
- **Docling** für Dokumentenverarbeitung mit ASR

### **Datenbank & Storage**
- **PostgreSQL 13+** primäre Datenbank
- **Redis** Caching und Echtzeit-Features
- **Weaviate** Vector-Embeddings und semantische Suche
- **Dateisystem** Dokument- und Medien-Storage

### **DevOps & Testing**
- **Docker & Docker Compose** Containerisierung
- **Pytest** umfassende Backend-Tests (90%+ Coverage)
- **Jest & Cypress** Frontend-Tests (95%+ Coverage)
- **GitHub Actions** CI/CD Pipeline
- **MkDocs** Dokumentation mit i18n-Unterstützung

## 📈 Performance-Metriken

### **Bewährte Performance**
- **Response Zeit**: < 100ms für Health Checks, < 500ms für API-Calls
- **Gleichzeitige Benutzer**: Unterstützt 100+ simultane Verbindungen
- **Speicher-Effizienz**: < 50MB Erhöhung unter Last
- **Dateiverarbeitung**: Verarbeitet 50MB+ Dateien effizient
- **Echtzeit-Messaging**: < 100ms Nachrichtenzustellung
- **Such-Performance**: Sub-Sekunden semantische Suchergebnisse
- **Cache-Hit-Rate**: 85%+ für häufig zugerufene Daten

### **Test-Coverage**
- **Backend Tests**: 90%+ Coverage mit Unit-, Integration- und Performance-Tests
- **Frontend Tests**: 95%+ Coverage mit Komponenten-, Service- und E2E-Tests
- **Performance Tests**: Load Testing und Memory Monitoring
- **Security Tests**: Authentifizierung, Autorisierung und Input-Validierung

## 🚀 Deployment-Optionen

### **Docker (Empfohlen)**
```bash
# Entwicklung
docker-compose up --build

# Produktion
docker-compose -f docker-compose.prod.yml up -d
```

### **Manuelles Setup**
```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend-react
npm install
npm run dev
```

### **Produktions-Deployment**
- **Environment-Konfiguration**: Umfassende Umgebungsvariablen-Setup
- **Security-Hardening**: JWT-Tokens, CORS, Rate-Limiting
- **Performance-Optimierung**: Caching, Connection-Pooling
- **Monitoring**: Health Checks und Performance-Tracking

## 🎯 Seiten & Benutzeroberfläche

ConvoSphere bietet eine umfassende Web-Oberfläche mit folgenden Seiten:

- **🏠 Dashboard** - Überblick, Statistiken und Schnellaktionen
- **💬 Chat** - Haupt-Chat-Interface mit AI-Assistenten
- **📚 Knowledge Base** - Dokumenten-Management und Suche
- **🤖 Assistants** - AI-Assistenten-Erstellung und -Management
- **🔧 Tools** - Tool-Integration und MCP-Management *(Demo-/Entwicklungsdaten)*
- **👤 Profile** - Benutzerprofil und Einstellungen
- **⚙️ Settings** - Anwendungskonfiguration
- **🔐 Authentication** - Login und Registrierung mit SSO-Optionen
- **👨‍💼 Admin** - Administratives Dashboard *(Demo-/Entwicklungsdaten)*
- **💬 Conversations** - Konversationsverlauf und -management
- **🔧 MCP Tools** - Model Context Protocol Tools
- **📊 System Status** - Echtzeit-System-Monitoring

**Hinweis**: Admin-Dashboard und Tools-Seiten verwenden derzeit Demo-/Entwicklungsdaten zur UI-Demonstration.

## 🤝 Contributing

Wir freuen uns über Beiträge! ConvoSphere wurde mit modernen Entwicklungspraktiken erstellt:

- **Code-Qualität**: ESLint, Prettier, Type-Safety mit TypeScript
- **Testing**: Umfassende Test-Suites mit hoher Coverage
- **Dokumentation**: Zweisprachige Dokumentation (EN/DE)
- **CI/CD**: Automatisierte Test- und Deployment-Pipelines

Siehe [Contributing Guide](../project/contributing.md) für detaillierte Informationen.

## 📄 License

MIT License - siehe [LICENSE](../../../LICENSE) für Details.

## 🆘 Support & Community

- **📚 Dokumentation**: Umfassende Guides und API-Referenz
- **🐛 Issues**: [GitHub Issues](https://github.com/your-org/convosphere/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/your-org/convosphere/discussions)
- **🎮 Discord**: [Community Server](https://discord.gg/your-server)

---

<div align="center">

**Bereit zum Starten?** [Quick Start →](quick-start.md)

**Detaillierte Anleitung?** [User Guide →](user-guide.md) | [Developer Guide →](developer-guide.md)

**Features erkunden:** [Knowledge Base →](../features/knowledge-base.md) | [AI Integration →](../features/ai-integration.md) | [Tools →](../features/tools.md)

**Mit ❤️ erstellt vom ConvoSphere Team**

</div>