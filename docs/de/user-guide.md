# Benutzer-Guide - ConvoSphere verwenden

## 🎯 Überblick

ConvoSphere ist eine umfassende AI-Chat-Plattform mit einer erweiterten Knowledge Base, Echtzeit-Messaging, leistungsstarken AI-Assistenten und Enterprise-Features. Dieser Guide zeigt Ihnen, wie Sie alle Funktionen effektiv nutzen.

## 🏠 Dashboard

Das Dashboard ist Ihre zentrale Anlaufstelle mit:

- **System-Überblick**: Wichtige Statistiken und Metriken
- **Schnellaktionen**: Schneller Zugriff zum Erstellen neuer Chats, Dokumente hochladen oder Assistenten verwalten
- **Aktuelle Aktivitäten**: Neueste Konversationen, Uploads und Systemaktivitäten
- **Performance-Metriken**: Echtzeit-Systemgesundheit und Nutzungsstatistiken
- **Benutzer-Analytics**: Ihre Aktivitätszusammenfassung und Nutzungsmuster

**Navigation**: Zugang über das Home-Symbol in der Seitenleiste oder gehen Sie zu `/dashboard`

## 💬 Chat-Interface

### Konversationen starten

**Mehrere Wege zum Chat:**
1. **Dashboard** → "Neuer Chat" oder "Neue Konversation" Button
2. **Chat-Seite** → "+" Button in der Seitenleiste
3. **Direkte Navigation** → Gehen Sie zu `/` (Standard-Route)
4. **Seitenleiste** → Klicken Sie auf "Chat" in der Navigation

### Nachrichten senden

- **Text-Eingabe**: Tippen Sie in das Nachrichteneingabefeld unten
- **Senden**: Drücken Sie `Enter` zum sofortigen Senden
- **Neue Zeile**: Verwenden Sie `Shift+Enter` für Zeilenumbrüche
- **Datei-Anhänge**: Klicken Sie auf das Büroklammer-Symbol zum Anhängen von Dateien
- **Spracheingabe**: Verwenden Sie das Mikrofon-Symbol für Speech-to-Text

### Chat-Funktionen

#### **Echtzeit-Features**
- **Sofortige Zustellung**: Nachrichten erscheinen sofort via WebSocket
- **Schreibindikatoren**: Sehen Sie, wann AI-Assistenten antworten
- **Status-Updates**: Echtzeit-Verbindungs- und Verarbeitungsstatus
- **Live-Benachrichtigungen**: Sofortige Alerts für neue Nachrichten

#### **Datei-Anhänge**
**Unterstützte Formate:**
- **PDF** (.pdf) - Vollständige Textextraktion und -verarbeitung
- **Word-Dokumente** (.docx) - Komplette Dokumentenanalyse
- **Textdateien** (.txt) - Direkte Textverarbeitung
- **Markdown** (.md) - Formatierter Text mit Strukturerhaltung

**Features:**
- **Größenlimit**: Bis zu 50MB pro Datei
- **Drag & Drop**: Ziehen Sie Dateien einfach in den Chat
- **Bulk-Upload**: Wählen Sie mehrere Dateien gleichzeitig
- **Verarbeitungsstatus**: Echtzeit-Upload und Verarbeitungsfeedback

#### **Nachrichtenformatierung**
- **Markdown-Unterstützung**: Verwenden Sie *kursiv*, **fett**, `code`, und mehr
- **Code-Blöcke**: Syntax-Highlighting für Programmiersprachen
- **Listen**: Nummerierte und Aufzählungslisten
- **Tabellen**: Formatierte Datendarstellung
- **Links**: Automatische Link-Erkennung und -formatierung

#### **Chat-Management**
- **Nachrichtenverlauf**: Alle Konversationen automatisch gespeichert
- **Suche**: Finden Sie spezifische Nachrichten oder Themen
- **Export**: Konversationsverlauf herunterladen
- **Konversations-Threading**: Organisierte Nachrichtenabläufe

## 📚 Knowledge Base

### Dokumenten-Management

#### **Dokumente hochladen**
1. **Navigation**: Gehen Sie zur Knowledge Base Seite (`/knowledge-base`)
2. **Upload-Methoden**:
   - **Drag & Drop**: Dateien direkt auf den Upload-Bereich ziehen
   - **Datei-Browser**: Klicken Sie "Upload" zum Auswählen von Dateien
   - **Bulk-Import**: Mehrere Dateien gleichzeitig auswählen
3. **Dokumenten-Metadaten**:
   - **Titel**: Benutzerdefinierter Dokumententitel
   - **Beschreibung**: Dokumentenzusammenfassung oder Notizen
   - **Tags**: Kategorisierungs-Labels
   - **Kategorie**: Dokumenten-Klassifizierung
4. **Verarbeitung**: Automatische Textextraktion und Chunking

#### **Erweiterte Upload-Features**
- **Bulk-Operationen**: Dutzende von Dateien auf einmal hochladen
- **Fortschritts-Tracking**: Echtzeit-Upload und Verarbeitungsstatus
- **Fehlerbehandlung**: Klares Feedback bei fehlgeschlagenen Uploads
- **Duplikat-Erkennung**: Automatische Erkennung von doppeltem Inhalt
- **Metadaten-Auto-Extraktion**: Automatische Titel- und Beschreibungsgenerierung

### Dokumenten-Organisation

#### **Tag-Management**
- **Tag-Erstellung**: Erstellen Sie benutzerdefinierte Tags zur Organisation
- **Tag-Clouds**: Visuelle Darstellung der Tag-Popularität
- **Tag-Statistiken**: Nutzungsanalysen und Einblicke
- **Bulk-Tagging**: Tags auf mehrere Dokumente anwenden
- **System-Tags**: Vordefinierte Organisationskategorien

#### **Erweiterte Suche**
- **Semantische Suche**: AI-gestützte Content-Entdeckung
- **Volltext-Suche**: Finden Sie exakte Phrasen und Begriffe
- **Tag-Filterung**: Filtern nach einzelnen oder mehreren Tags
- **Metadaten-Filter**: Suche nach Autor, Datum, Dateityp
- **Erweiterte Operatoren**: Komplexe Suchanfragen
- **Such-Verlauf**: Vorherige Suchergebnisse und Anfragen

#### **Dokumenten-Aktionen**
- **Ansicht**: Vorschau von Dokumenteninhalt und Metadaten
- **Bearbeiten**: Dokumenteninformationen und Tags ändern
- **Download**: Original-Dateien abrufen
- **Löschen**: Dokumente entfernen (mit Bestätigung)
- **Neu verarbeiten**: Inhalt neu extrahieren und chunken
- **Teilen**: Dokumentenzugriff und Berechtigungen kontrollieren

### Rollenbasierter Zugriff

ConvoSphere implementiert ein umfassendes rollenbasiertes Zugriffssystem:

| Funktion | User | Premium | Moderator | Admin |
|---------|------|---------|-----------|-------|
| Dokumente hochladen | ✓ | ✓ | ✓ | ✓ |
| Eigene Dokumente verwalten | ✓ | ✓ | ✓ | ✓ |
| Bulk-Import | ✗ | ✓ | ✓ | ✓ |
| Tag-Management | ✗ | ✓ | ✓ | ✓ |
| System-Tags erstellen | ✗ | ✗ | ✗ | ✓ |
| Alle Dokumente einsehen | ✗ | ✗ | ✓ | ✓ |
| Benutzerverwaltung | ✗ | ✗ | ✗ | ✓ |
| System-Statistiken | ✗ | ✗ | ✗ | ✓ |

### AI-Integration mit Knowledge Base

#### **Kontextbewusste Antworten**
- **Automatischer Kontext**: AI verwendet automatisch relevante Dokumente
- **Manuelle Auswahl**: Wählen Sie spezifische Dokumente für Kontext
- **Quellen-Zitate**: AI-Antworten enthalten Dokumentenreferenzen
- **Inhaltszusammenfassung**: AI erstellt Zusammenfassungen großer Dokumente

#### **Intelligente Dokumenten-Entdeckung**
- **Semantisches Matching**: AI findet relevanten Inhalt basierend auf Bedeutung
- **Themen-Assoziation**: Verwandte Dokumente werden automatisch vorgeschlagen
- **Inhalts-Ranking**: Relevanteste Dokumente werden priorisiert
- **Kontext-Fenster**: Optimale Inhalts-Chunks für AI-Verarbeitung

## 🤖 AI-Assistenten

### Benutzerdefinierte Assistenten erstellen

1. **Navigation**: Gehen Sie zur Assistenten-Seite (`/assistants`)
2. **Assistent erstellen**: Klicken Sie "Neuen Assistenten erstellen"
3. **Konfigurations-Optionen**:
   - **Name & Beschreibung**: Assistenten-Identität
   - **AI-Modell-Auswahl**: Wählen Sie aus verfügbaren Anbietern
   - **Persönlichkeits-Einstellungen**: Definieren Sie Antwort-Stil und Verhalten
   - **Knowledge Base-Verknüpfung**: Mit spezifischen Dokumenten verbinden
   - **Tool-Zugriff**: Spezifische Tools und Fähigkeiten aktivieren
   - **Antwort-Parameter**: Temperatur, max. Tokens, etc.

### Assistenten-Management

#### **Verfügbare Features**
- **Template-Bibliothek**: Vorgefertigte Assistenten-Templates
- **Benutzerdefinierte Persönlichkeiten**: Definieren Sie einzigartige Antwort-Stile
- **Multi-Modell-Unterstützung**: OpenAI, Anthropic und andere Anbieter
- **Performance-Tuning**: Antwort-Qualität und -geschwindigkeit anpassen
- **Nutzungs-Analytics**: Assistenten-Performance und -nutzung verfolgen
- **Sharing-Optionen**: Assistenten mit anderen Benutzern teilen

#### **Assistenten verwenden**
- **Chat-Auswahl**: Assistent aus Dropdown im Chat wählen
- **Direkte Erwähnung**: Verwenden Sie `@AssistentenName` um spezifische Assistenten aufzurufen
- **Standard-Assistent**: Setzen Sie Ihren bevorzugten Standard-Assistenten
- **Kontext-Wechsel**: Assistenten mitten in der Konversation wechseln
- **Assistenten-Vergleich**: Mehrere Assistenten gleichzeitig testen

## 🔧 Tools & Integrationen

### Model Context Protocol (MCP) Tools

Navigieren Sie zu **Tools** (`/tools`) oder **MCP Tools** (`/mcp-tools`) um zuzugreifen:

#### **Verfügbare Tool-Kategorien**
- **Such-Tools**: Web-Suche, Dokumentensuche, semantische Suche
- **Rechner**: Mathematische Berechnungen und Analysen
- **Dateiverarbeitung**: Dokumentenanalyse, Format-Konvertierung
- **API-Integrationen**: Externe Service-Verbindungen
- **Datenanalyse**: Statistische Analyse und Visualisierung
- **Benutzerdefinierte Tools**: Benutzerdefinierte Tool-Implementierungen

#### **Tool-Management**
- **Tool-Entdeckung**: Verfügbare Tools durchsuchen
- **Installation**: Neue Tools zu Ihrem Arbeitsbereich hinzufügen
- **Konfiguration**: Tool-Parameter und Anmeldedaten einrichten
- **Ausführungs-Tracking**: Tool-Nutzung und -performance überwachen
- **Benutzerdefinierte Entwicklung**: Erstellen Sie Ihre eigenen Tools
- **Performance-Metriken**: Tool-Ausführungsstatistiken

#### **Tools im Chat verwenden**
- **Tool-Aufruf**: AI wählt automatisch passende Tools
- **Manuelle Auswahl**: Explizit spezifische Tools anfordern
- **Tool-Verkettung**: Mehrere Tools für komplexe Aufgaben kombinieren
- **Ergebnis-Integration**: Tool-Ausgaben in Konversationen integriert
- **Fehlerbehandlung**: Klares Feedback bei Tool-Ausführungsproblemen

## 👤 Profil & Einstellungen

### Profil-Management (`/profile`)

**Persönliche Informationen**:
- **Name & E-Mail**: Ihre Kontaktinformationen aktualisieren
- **Avatar**: Profilbild hochladen und verwalten
- **Sprach-Präferenz**: Interface-Sprache wählen (EN/DE)
- **Zeitzone**: Ihre lokale Zeitzone einstellen
- **Benachrichtigungs-Präferenzen**: Alert-Einstellungen konfigurieren

### Anwendungs-Einstellungen (`/settings`)

**Interface-Anpassung**:
- **Theme-Auswahl**: Zwischen dunklen und hellen Themes wechseln
- **Sprache**: Interface-Sprache ändern
- **Standard-Assistent**: Ihren bevorzugten AI-Assistenten einstellen
- **Chat-Präferenzen**: Standard-Chat-Verhalten konfigurieren
- **Performance-Einstellungen**: UI-Performance-Optionen anpassen

### Benachrichtigungen

**Benachrichtigungs-Typen**:
- **E-Mail-Benachrichtigungen**: E-Mail-Alerts konfigurieren
- **Browser-Benachrichtigungen**: In-App-Benachrichtigungseinstellungen
- **Mobile Push**: Push-Benachrichtigungs-Präferenzen (falls anwendbar)
- **Häufigkeits-Kontrolle**: Benachrichtigungshäufigkeits-Limits setzen
- **Typ-Filterung**: Wählen Sie, welche Ereignisse Benachrichtigungen auslösen

## 🔐 Authentifizierung & Sicherheit

### Account-Management

**Registrierung** (`/register`):
- **Account-Erstellung**: Neues Benutzerkonto erstellen
- **E-Mail-Verifizierung**: E-Mail-Adresse verifizieren
- **Profil-Setup**: Initiale Profilkonfiguration
- **Rollen-Zuweisung**: Automatische Rollenzuweisung

**Login** (`/login`):
- **Standard-Login**: E-Mail/Passwort-Authentifizierung
- **Angemeldet bleiben**: Persistente Login-Sessions
- **Passwort-Wiederherstellung**: Vergessene Passwörter zurücksetzen
- **Sicherheits-Features**: Schutz vor fehlgeschlagenen Login-Versuchen

### Sicherheits-Features

- **JWT-Authentifizierung**: Sichere token-basierte Authentifizierung
- **Session-Management**: Automatisches Session-Timeout und -erneuerung
- **Passwort-Sicherheit**: Starke Passwort-Anforderungen
- **Zwei-Faktor-Authentifizierung**: Erweiterte Sicherheitsoptionen (falls aktiviert)
- **Audit-Logging**: Account-Sicherheitsereignisse verfolgen

## 👨‍💼 Admin-Features (Nur für Admins)

### Admin-Dashboard (`/admin`)

**System-Überblick**:
- **Benutzerverwaltung**: Benutzerkonten erstellen, bearbeiten und verwalten
- **Rollen-Zuweisung**: Benutzerrollen zuweisen und ändern
- **System-Statistiken**: Umfassende Nutzungsanalysen
- **Performance-Monitoring**: Echtzeit-Systemgesundheits-Metriken
- **Audit-Logs**: Sicherheits- und Nutzungs-Audit-Pfade

### System-Monitoring (`/admin/system-status`)

**Echtzeit-Metriken**:
- **System-Gesundheit**: Server-Status und -performance
- **Datenbank-Performance**: Verbindungs- und Abfrage-Metriken
- **Speicher-Nutzung**: RAM- und Storage-Auslastung
- **Benutzer-Aktivität**: Aktive Benutzer und Session-Statistiken
- **Fehler-Tracking**: System-Fehler und Lösungsstatus

### Administrative Tools

- **Benutzer-Analytics**: Detaillierte Benutzerverhalten-Analyse
- **Content-Moderation**: Benutzercontent überprüfen und verwalten
- **System-Konfiguration**: Globale System-Einstellungen anpassen
- **Backup-Management**: Daten-Backup und -wiederherstellungsoptionen
- **Integrations-Management**: Externe Service-Konfigurationen

## 💬 Konversations-Management (`/conversations`)

### Konversations-Verlauf

**Features**:
- **Vollständiger Verlauf**: Zugriff auf alle vergangenen Konversationen
- **Suchen & Filtern**: Spezifische Konversationen finden
- **Organisation**: Nach Datum, Assistent oder Thema sortieren
- **Favoriten**: Wichtige Konversationen markieren
- **Archive**: Langzeit-Konversations-Speicherung

### Konversations-Aktionen

- **Fortsetzen**: Vorherige Konversationen wieder aufnehmen
- **Export**: Konversations-Transkripte herunterladen
- **Teilen**: Konversationen mit anderen Benutzern teilen
- **Duplizieren**: Kopien von Konversationen erstellen
- **Löschen**: Unerwünschte Konversationen entfernen

## 🎨 Benutzererfahrungs-Features

### Theme & Anpassung

- **Dark/Light Mode**: Zwischen Themes umschalten
- **System-Präferenz**: Automatisches Theme basierend auf OS-Einstellungen
- **Benutzerdefinierte Farben**: Interface-Farben personalisieren
- **Layout-Optionen**: Seitenleiste und Layout-Präferenzen anpassen
- **Barrierefreiheit**: Hoher Kontrast und Screen-Reader-Unterstützung

### Performance-Features

- **Lazy Loading**: Schnelles Seitenladen mit Code-Splitting
- **Echtzeit-Updates**: Sofortige UI-Updates via WebSocket
- **Offline-Unterstützung**: Eingeschränkte Funktionalität offline
- **Mobile-Optimierung**: Responsive Design für alle Geräte
- **Progressives Laden**: Schrittweises Content-Laden für bessere UX

### Internationalisierung

- **Sprach-Unterstützung**: Vollständige englische und deutsche Übersetzungen
- **Locale-Anpassung**: Datum-, Zeit- und Zahlenformatierung
- **Kulturelle Anpassung**: UI-Muster für verschiedene Kulturen angepasst
- **Einfaches Wechseln**: Sofortiges Sprach-Switching ohne Neuladen

## 🆘 Fehlerbehebung

### Häufige Probleme

**Verbindungsprobleme**:
- Internet-Konnektivität überprüfen
- WebSocket-Verbindungsstatus verifizieren
- Browser aktualisieren oder Anwendung neu starten

**Upload-Probleme**:
- Dateigröße unter 50MB-Limit verifizieren
- Dateiformat wird unterstützt überprüfen
- Ausreichenden Speicherplatz sicherstellen

**Performance-Probleme**:
- Browser-Cache und Cookies löschen
- Unnötige Browser-Tabs schließen
- Systemressourcen überprüfen (RAM, CPU)

### Hilfe bekommen

- **Dokumentation**: Umfassende Guides und FAQ
- **Support-Tickets**: Probleme über das System melden
- **Community**: Discord-Server und GitHub-Diskussionen
- **Fehlermeldungen**: Klare, umsetzbare Fehlerbeschreibungen

---

**Bereit zum Starten?** Beginnen Sie mit dem [Quick Start Guide](quick-start.md) oder erkunden Sie das [Dashboard](/) um alle Features in Aktion zu sehen!