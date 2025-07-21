# Entwicklungs-Roadmap: Erweiterung um moderne AI-Chat-Features

## Ziel
Diese Roadmap beschreibt die geplanten Erweiterungen, um das Projekt an den Funktionsumfang moderner Open-Source-AI-Chat-Apps anzugleichen. Die Umsetzung erfolgt schrittweise und beginnt erst, wenn die Basis stabil und fehlerfrei läuft.

---

## Funktionsvergleich (IST/SOLL)

**Bereits (teilweise) vorhanden:**
- Datei-Upload & RAG
- Websuche-Integration
- Plugin-/Function-Calling-System
- Conversation Memory
- Multi-Chat
- Rollen- & Rechteverwaltung

**Geplant:**
- Multi-Modell-Unterstützung (nahtloses Umschalten)
- Conversation Branching (Forks)
- Tabbed Chat (Frontend)
- Text-zu-Bild-Generierung
- Code-Interpreter/Sandbox
- Sprachein- & -ausgabe (STT/TTS)
- Multichannel-Integration (Slack, Telegram, etc.)
- Erweiterungs-/Marketplace-Ökosystem
- Export- & Sharing-Funktionen
- OpenAI-kompatible API & Provider-Wechsel
- Token-Streaming in Echtzeit
- RBAC-Feingranularität

---

## Phasenplan

### Phase 1: Grundlagen & Infrastruktur
- Multi-Modell-Unterstützung
- Conversation Branching
- Tabbed Chat

### Phase 2: Advanced AI Features
- Text-to-image generation
- Code interpreter / run-code cell
- Speech-to-text & text-to-speech (STT/TTS)
- **Performance Monitoring & System Status**
  - Integration of OpenTelemetry (OTLP) for tracing and metrics
  - API endpoint for system status & performance (admin only)
  - Admin UI with time-based visualizations (CPU, RAM, service status)
  - Live updates and tracing IDs

### Phase 3: Integration & Ökosystem
- Multichannel-Integration
- Erweiterungs-/Marketplace-Ökosystem
- Export- & Sharing-Funktionen
- OpenAI-kompatible API & Provider-Wechsel

### Phase 4: Feinschliff & UX
- Token-Streaming in Echtzeit
- RBAC-Feingranularität

---

## Hinweise zur Umsetzung
- Modularisierung aller neuen Features
- Nutzung etablierter Open-Source-Bibliotheken
- Testabdeckung für alle neuen Features
- Laufende Dokumentation im Sourcecode und in der User-Doku
- Regelmäßige, sprechende Commits

---

**Die Umsetzung der neuen Features beginnt erst nach erfolgreicher Stabilisierung und Absicherung der bestehenden Basis.**
