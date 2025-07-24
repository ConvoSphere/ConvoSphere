# Knowledge Base Verbesserungen

## Übersicht

Die Knowledge Base wurde umfassend erweitert und verbessert, um eine robustere, skalierbare und benutzerfreundlichere Lösung für Dokumentenverwaltung und RAG-Funktionalität zu bieten.

## Implementierte Verbesserungen

### 1. Strukturierte Tags und Metadaten

#### Neue Tag-Tabelle
- **Tag-Modell**: Eigene Tabelle für Tags mit normalisierten Namen
- **Many-to-Many-Relation**: Zwischen Dokumenten und Tags
- **Tag-Statistiken**: Verwendungszähler und System-Tags
- **Tag-Normalisierung**: Automatische Vereinheitlichung (Kleinschreibung, Trimmen)

#### Erweiterte Dokumenten-Metadaten
- **Strukturierte Felder**: Autor, Quelle, Sprache, Jahr, Version, Keywords
- **Dokumententypen**: Kategorisierung (PDF, DOCUMENT, TEXT, SPREADSHEET, etc.)
- **Verarbeitungs-Metadaten**: Engine, Optionen, Statistiken
- **Inhalts-Statistiken**: Seitenanzahl, Wortanzahl, Zeichenanzahl

### 2. Asynchrone Verarbeitung

#### Background Job Service
- **Job-Queue**: Prioritätsbasierte Verarbeitung
- **Mehrere Worker**: Parallele Verarbeitung mehrerer Dokumente
- **Job-Tracking**: Fortschritt, Status, Fehlerbehandlung
- **Retry-Mechanismus**: Automatische Wiederholung fehlgeschlagener Jobs

#### Job-Typen
- **Process**: Standard-Dokumentenverarbeitung
- **Reprocess**: Neuverarbeitung mit anderen Optionen
- **Bulk Import**: Massenimport mehrerer Dokumente

### 3. Erweiterte Suche und Filterung

#### Strukturierte Filter
- **Dokumententyp**: Filter nach PDF, Word, etc.
- **Autor**: Suche nach Dokumentenautor
- **Jahr**: Zeitbasierte Filterung
- **Sprache**: Sprachbasierte Filterung
- **Tags**: Tag-basierte Filterung

#### Erweiterte Suchfunktionen
- **Semantische Suche**: Verbesserte Embedding-basierte Suche
- **Metadaten-Filter**: Strukturierte Filterung in Weaviate
- **Suchhistorie**: Tracking von Suchanfragen
- **Erweiterte Ergebnisse**: Mehr Kontext in Suchergebnissen

### 4. Verbesserte API

#### Neue Endpunkte
- **Tag-Management**: `/tags`, `/tags/search`
- **Dokumenten-Updates**: `PUT /documents/{id}`
- **Verarbeitungs-Jobs**: `/processing/jobs`
- **Bulk-Import**: `/bulk-import`
- **Statistiken**: `/stats`
- **Erweiterte Suche**: `/search/advanced`

#### Erweiterte Schemas
- **Tag-Schemas**: TagResponse, TagList, TagCreate
- **Job-Schemas**: DocumentProcessingJobResponse, DocumentProcessingJobList
- **Erweiterte Dokumenten-Schemas**: Mit allen neuen Metadaten
- **Filter-Schemas**: DocumentFilter, AdvancedSearchRequest

### 5. Datenbank-Optimierungen

#### Neue Tabellen
- **tags**: Tag-Verwaltung
- **document_tag_association**: Many-to-Many-Relation
- **document_processing_jobs**: Job-Tracking

#### Indexe
- **Performance-Optimierung**: Indexe auf häufig abgefragte Felder
- **Compound-Indexe**: Für komplexe Abfragen
- **Tag-Indexe**: Für schnelle Tag-Suche

#### Migration
- **Alembic-Migration**: Automatische Schema-Updates
- **Backward Compatibility**: Legacy-Felder bleiben erhalten

## Technische Details

### Datenmodell-Erweiterungen

```python
# Neue Tag-Tabelle
class Tag(Base):
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    color = Column(String(7))  # Hex color
    is_system = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)

# Erweiterte Dokumenten-Felder
class Document(Base):
    # Neue strukturierte Metadaten
    author = Column(String(255), index=True)
    source = Column(String(500))
    language = Column(String(10), index=True)
    year = Column(Integer, index=True)
    document_type = Column(String(50), index=True)
    processing_engine = Column(String(100))
    
    # Inhalts-Statistiken
    page_count = Column(Integer)
    word_count = Column(Integer)
    character_count = Column(Integer)
    
    # Many-to-Many-Relation zu Tags
    tags = relationship("Tag", secondary=document_tag_association)
```

### Service-Erweiterungen

```python
# Tag-Service für Tag-Management
class TagService:
    def normalize_tag_name(self, tag_name: str) -> str
    def get_or_create_tag(self, tag_name: str) -> Tag
    def get_tags(self, user_id: str, limit: int) -> List[Tag]
    def search_tags(self, query: str, user_id: str, limit: int) -> List[Tag]

# Metadaten-Extraktor
class MetadataExtractor:
    def extract_pdf_metadata(file_path: str) -> Dict[str, Any]
    def extract_word_metadata(file_path: str) -> Dict[str, Any]
    def detect_language(text: str) -> Optional[str]

# Background Job Service
class BackgroundJobService:
    def schedule_job(self, job_id: str, priority: int) -> bool
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]
    def cancel_job(self, job_id: str) -> bool
```

### API-Verwendung

#### Dokumenten-Upload mit Tags
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/documents" \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "title=Mein Dokument" \
  -F "tags=wichtig,projekt,2024" \
  -F "author=Max Mustermann" \
  -F "year=2024"
```

#### Erweiterte Suche
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/search/advanced" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Machine Learning",
    "filters": {
      "document_type": "pdf",
      "author": "Max Mustermann",
      "year": 2024,
      "tag_names": ["wichtig", "projekt"]
    },
    "limit": 20
  }'
```

#### Tag-Management
```bash
# Alle Tags abrufen
curl -X GET "http://localhost:8000/api/v1/knowledge/tags" \
  -H "Authorization: Bearer <token>"

# Tags suchen
curl -X GET "http://localhost:8000/api/v1/knowledge/tags/search?query=projekt" \
  -H "Authorization: Bearer <token>"
```

## Vorteile der Verbesserungen

### 1. Bessere Organisation
- **Strukturierte Tags**: Einfache Kategorisierung und Filterung
- **Metadaten-Extraktion**: Automatische Extraktion von Dokumenteninformationen
- **Dokumententypen**: Klare Kategorisierung verschiedener Dateitypen

### 2. Skalierbarkeit
- **Asynchrone Verarbeitung**: Nicht-blockierende Dokumentenverarbeitung
- **Job-Queue**: Prioritätsbasierte Verarbeitung großer Mengen
- **Parallele Verarbeitung**: Mehrere Dokumente gleichzeitig

### 3. Benutzerfreundlichkeit
- **Erweiterte Suche**: Präzise Filterung und Suche
- **Tag-System**: Intuitive Dokumentenorganisation
- **Fortschritts-Tracking**: Transparenz bei Verarbeitung

### 4. Performance
- **Datenbank-Indexe**: Schnellere Abfragen
- **Strukturierte Metadaten**: Effiziente Filterung
- **Optimierte Suche**: Verbesserte RAG-Performance

## Nächste Schritte

### Geplante Verbesserungen
1. **WebSocket-Support**: Echtzeit-Updates für Job-Status
2. **Erweiterte Metadaten**: Automatische Kategorisierung
3. **Dokumenten-Versionierung**: Versionskontrolle für Dokumente
4. **Berechtigungen**: Tag-basierte Zugriffskontrolle
5. **Export-Funktionen**: Export von Dokumenten und Metadaten

### Migration
1. **Datenbank-Migration ausführen**:
   ```bash
   alembic upgrade head
   ```

2. **Background Service starten**:
   ```python
   from app.services.background_job_service import start_background_job_service
   start_background_job_service()
   ```

3. **Legacy-Daten migrieren** (optional):
   - Bestehende JSON-Tags in neue Tag-Tabelle übertragen
   - Metadaten aus bestehenden Dokumenten extrahieren

## Fazit

Die Knowledge Base Verbesserungen bieten eine solide Grundlage für:
- **Skalierbare Dokumentenverwaltung**
- **Effiziente RAG-Prozesse**
- **Benutzerfreundliche Organisation**
- **Robuste asynchrone Verarbeitung**

Die Implementierung ist rückwärtskompatibel und kann schrittweise eingeführt werden.