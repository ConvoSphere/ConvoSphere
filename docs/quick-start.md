# Quick Start - In 5 Minuten einsatzbereit

## 🚀 Schneller Start mit Docker

### 1. Repository klonen
```bash
git clone https://github.com/your-org/convosphere.git
cd convosphere
```

### 2. Mit Docker starten
```bash
docker-compose up --build
```

### 3. Browser öffnen
→ [http://localhost:5173](http://localhost:5173)

**Das war's!** 🎉

## 📝 Erste Schritte

### 1. Registrierung
- Klicken Sie auf "Register" in der oberen rechten Ecke
- Füllen Sie das Formular aus
- Bestätigen Sie Ihre E-Mail

### 2. Erste Konversation
- Klicken Sie auf "New Chat" oder "Neue Konversation"
- Schreiben Sie eine Nachricht
- Die AI antwortet automatisch

### 3. Knowledge Base nutzen
- Gehen Sie zu "Knowledge Base"
- Laden Sie ein PDF oder DOCX hoch
- Fragen Sie die AI über den Inhalt

## 🔧 Alternative: Manueller Setup

### Voraussetzungen
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Backend starten
```bash
# Backend-Verzeichnis
cd backend

# Dependencies installieren
pip install -r requirements.txt

# Environment konfigurieren
cp env.example .env
# .env bearbeiten mit Ihren Einstellungen

# Datenbank-Migrationen
alembic upgrade head

# Backend starten
uvicorn app.main:app --reload
```

### Frontend starten
```bash
# Frontend-Verzeichnis
cd frontend-react

# Dependencies installieren
npm install

# Frontend starten
npm run dev
```

## 🐛 Häufige Probleme

### Port bereits belegt
```bash
# Ports prüfen
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# Andere Ports verwenden
docker-compose -f docker-compose.yml -p convosphere up
```

### Docker-Probleme
```bash
# Docker neu starten
docker system prune -a
docker-compose down
docker-compose up --build
```

### Datenbank-Probleme
```bash
# Datenbank zurücksetzen
docker-compose down -v
docker-compose up --build
```

## 📚 Nächste Schritte

- **[User Guide](user-guide.md)** - Alle Features kennenlernen
- **[FAQ](faq.md)** - Häufige Fragen und Lösungen
- **[Developer Guide](developer-guide.md)** - Für Entwickler

## 🆘 Hilfe benötigt?

- **GitHub Issues**: [Bug melden](https://github.com/your-org/convosphere/issues)
- **Discord**: [Community Support](https://discord.gg/your-server)
- **Dokumentation**: [Vollständige Guides](../index.md)