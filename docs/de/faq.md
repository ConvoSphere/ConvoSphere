# FAQ - Häufige Fragen

## 🚀 Getting Started

### Wie starte ich ConvoSphere?
```bash
git clone https://github.com/your-org/convosphere.git
cd convosphere
docker-compose up --build
```
Dann [http://localhost:5173](http://localhost:5173) öffnen.

### Welche Voraussetzungen brauche ich?
- **Docker** und **Docker Compose**
- **Git**
- **Browser** (Chrome, Firefox, Safari, Edge)

### Funktioniert es auch ohne Docker?
Ja, siehe [Quick Start](quick-start.md#alternative-manueller-setup) für manuellen Setup.

## 💬 Chat & Konversationen

### Wie starte ich eine neue Konversation?
- **Dashboard** → "New Chat" Button
- **Chat-Seite** → "+" in der Seitenleiste
- **Direktlink** → `/chat` in der URL

### Kann ich Dateien in den Chat hochladen?
Ja, unterstützte Formate:
- PDF (.pdf)
- Word (.docx) 
- Text (.txt)
- Markdown (.md)

**Größenlimit:** 50MB pro Datei

### Werden meine Konversationen gespeichert?
Ja, alle Konversationen werden automatisch gespeichert und sind nur für Sie sichtbar.

### Kann ich meine Chat-Historie durchsuchen?
Ja, nutzen Sie die **globale Suche** (Ctrl/Cmd + K) oder die **Suche in der Chat-Seite**.

## 📚 Knowledge Base

### Welche Dateitypen kann ich hochladen?
- **PDF** (.pdf) - Volltext-Extraktion
- **Word** (.docx) - Volltext-Extraktion  
- **Text** (.txt) - Direkt verwendbar
- **Markdown** (.md) - Formatierung erhalten
- **CSV** (.csv) - Tabellendaten
- **JSON** (.json) - Strukturierte Daten

### Wie groß können meine Dateien sein?
**Maximal 50MB** pro Datei. Für größere Dokumente empfehlen wir, diese zu teilen.

### Wie funktioniert die semantische Suche?
Die AI analysiert den Inhalt Ihrer Dokumente und findet ähnliche Konzepte, auch wenn die exakten Wörter nicht übereinstimmen.

### Kann ich meine Dokumente mit anderen teilen?
Aktuell sind Dokumente **privat**. Sharing-Features sind in Entwicklung.

### Wie organisiere ich meine Dokumente?
- **Tags** - Dokumente kategorisieren
- **Metadaten** - Titel, Beschreibung, Autor
- **Ordner** - Virtuelle Organisation (in Entwicklung)

## 🤖 AI & Assistenten

### Welche AI-Modelle werden unterstützt?
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3, Claude-2
- **Andere**: Über LiteLLM konfigurierbar

### Wie erstelle ich einen eigenen Assistenten?
1. **Assistants** → "Create Assistant"
2. **Name und Beschreibung** eingeben
3. **AI-Modell** wählen
4. **Persönlichkeit** definieren
5. **Knowledge Base** verknüpfen (optional)

### Kann ich zwischen verschiedenen Assistenten wechseln?
Ja, nutzen Sie das **Dropdown-Menü** im Chat oder sprechen Sie Assistenten direkt an mit "@Name".

### Warum antwortet die AI manchmal nicht?
Mögliche Ursachen:
- **API-Limits** erreicht
- **Internet-Verbindung** gestört
- **AI-Provider** temporär nicht verfügbar
- **Rate Limiting** aktiv

## 🛠️ Tools & Features

### Welche Tools sind verfügbar?
- **Web-Suche** - Aktuelle Informationen
- **Rechner** - Mathematische Berechnungen
- **Code-Interpreter** - Code ausführen
- **Datei-Operationen** - Dateien bearbeiten

### Wie verwende ich Tools?
1. **Tool auswählen** in der Tool-Palette
2. **Parameter eingeben** (falls erforderlich)
3. **Ausführen** - Tool wird automatisch ausgeführt

### Kann ich eigene Tools erstellen?
Ja, für **Entwickler** über das MCP (Model Context Protocol) Framework.

## 👥 Benutzer & Rollen

### Welche Benutzerrollen gibt es?
- **Standard User** - Grundfunktionen
- **Premium User** - Erweiterte Features
- **Moderator** - Community-Management
- **Admin** - Vollzugriff

### Wie ändere ich mein Passwort?
**Profil** → "Change Password" → Neues Passwort eingeben.

### Kann ich meinen Account löschen?
Ja, **Profil** → "Delete Account" → Bestätigung.

### Wer kann meine Daten sehen?
- **Sie selbst** - Alle Ihre Daten
- **Admins** - Nur bei Support-Anfragen
- **Niemand sonst** - Ihre Daten sind privat

## 🔒 Sicherheit & Datenschutz

### Sind meine Daten sicher?
Ja:
- **Ende-zu-Ende-Verschlüsselung** für Nachrichten
- **Sichere Speicherung** in der Cloud
- **Regelmäßige Backups** automatisch

### Ist ConvoSphere DSGVO-konform?
Ja, wir halten uns an die europäischen Datenschutzrichtlinien.

### Kann ich meine Daten exportieren?
Ja, **Profil** → "Export Data" → Alle Ihre Daten herunterladen.

### Werden meine Daten an Dritte weitergegeben?
**Nein**, Ihre Daten bleiben bei uns und werden nicht an Dritte weitergegeben.

## 🐛 Technische Probleme

### Die Seite lädt nicht
1. **Browser aktualisieren** (F5)
2. **Cache leeren** (Ctrl+Shift+R)
3. **Anderen Browser** versuchen
4. **Docker-Container** neu starten

### Chat funktioniert nicht
1. **WebSocket-Verbindung** prüfen
2. **Browser-Konsole** auf Fehler prüfen
3. **Internet-Verbindung** testen
4. **Docker-Logs** prüfen

### Upload fehlgeschlagen
1. **Dateigröße** prüfen (max. 50MB)
2. **Dateiformat** überprüfen
3. **Browser-Cache** leeren
4. **Docker-Container** neu starten

### Performance-Probleme
1. **Browser schließen** und neu öffnen
2. **Anderen Browser** versuchen
3. **Docker-Ressourcen** prüfen
4. **System-Ressourcen** überprüfen

## 📱 Mobile & Browser

### Funktioniert es auf dem Handy?
Ja, ConvoSphere ist **mobile-optimiert** und funktioniert auf allen Geräten.

### Welche Browser werden unterstützt?
- **Chrome** (empfohlen)
- **Firefox**
- **Safari**
- **Edge**

### Gibt es eine App?
Aktuell nur **Web-App**, native Apps sind in Entwicklung.

### Funktioniert es offline?
**Grundfunktionen** funktionieren offline, aber AI und Upload benötigen Internet.

## 💰 Kosten & Limits

### Ist ConvoSphere kostenlos?
**Ja**, die Grundversion ist kostenlos.

### Gibt es Limits?
- **Dateigröße**: 50MB pro Datei
- **Upload**: 100 Dateien pro Tag
- **Chat**: 1000 Nachrichten pro Tag
- **API-Calls**: 1000 pro Stunde

### Was ist in der Premium-Version?
- **Größere Limits**
- **Erweiterte AI-Modelle**
- **Bulk-Import**
- **Prioritäts-Support**

## 🆘 Support & Hilfe

### Wo bekomme ich Hilfe?
- **Diese FAQ** - Häufige Fragen
- **User Guide** - Vollständige Anleitung
- **Discord Server** - Community-Support
- **GitHub Issues** - Bug melden

### Wie melde ich einen Bug?
1. **GitHub Issues** öffnen
2. **Problem beschreiben**
3. **Screenshots** hinzufügen
4. **Browser/System** angeben

### Gibt es einen Live-Chat?
Ja, für **Premium-User** während der Geschäftszeiten.

### Wo kann ich Feedback geben?
- **Discord Server** - Community-Feedback
- **GitHub Discussions** - Feature-Requests
- **E-Mail** - Direktes Feedback

## 🔮 Zukünftige Features

### Was kommt als nächstes?
- **Voice Integration** - Sprach-Eingabe/Ausgabe
- **Multi-Chat** - Parallele Konversationen
- **Code Interpreter** - Sichere Code-Ausführung
- **Mobile Apps** - Native iOS/Android Apps

### Kann ich Features vorschlagen?
Ja, über **GitHub Discussions** oder **Discord Server**.

### Wann kommen neue Features?
Neue Features werden **regelmäßig** veröffentlicht. Folgen Sie uns auf **GitHub** für Updates.

---

**Weitere Hilfe?** [User Guide](user-guide.md) | [Developer Guide](developer-guide.md) | [Support](../index.md)