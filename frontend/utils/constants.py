"""
Constants for the AI Assistant Platform frontend.

This module defines application-wide constants used throughout
the frontend application.
"""

# API Configuration
API_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 30.0

# Supported Languages
SUPPORTED_LANGUAGES = {
    "de": "Deutsch",
    "en": "English",
}

# Supported Themes
SUPPORTED_THEMES = {
    "light": "Hell",
    "dark": "Dunkel",
    "auto": "Automatisch",
}

# File Upload
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_FILE_TYPES = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "document": [".pdf", ".doc", ".docx", ".txt", ".md"],
    "data": [".csv", ".json", ".xml"],
    "archive": [".zip", ".rar"],
}

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Chat Configuration
MAX_MESSAGE_LENGTH = 4000
TYPING_INDICATOR_DELAY = 1000  # ms

# Assistant Configuration
DEFAULT_ASSISTANT_MODEL = "gpt-4"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096

# Error Messages
ERROR_MESSAGES = {
    "network_error": "Netzwerkfehler. Bitte überprüfe deine Verbindung.",
    "authentication_error": "Anmeldung fehlgeschlagen. Bitte überprüfe deine Anmeldedaten.",
    "permission_error": "Du hast keine Berechtigung für diese Aktion.",
    "validation_error": "Ungültige Eingabe. Bitte überprüfe deine Daten.",
    "server_error": "Serverfehler. Bitte versuche es später erneut.",
    "timeout_error": "Zeitüberschreitung. Bitte versuche es erneut.",
    "file_upload_error": "Datei-Upload fehlgeschlagen. Bitte versuche es erneut.",
    "conversation_error": "Fehler beim Laden der Konversation.",
    "assistant_error": "Fehler beim Laden des Assistenten.",
    "tool_error": "Fehler bei der Tool-Ausführung.",
}

# Success Messages
SUCCESS_MESSAGES = {
    "login_success": "Erfolgreich angemeldet!",
    "logout_success": "Erfolgreich abgemeldet!",
    "registration_success": "Konto erfolgreich erstellt!",
    "profile_updated": "Profil erfolgreich aktualisiert!",
    "assistant_created": "Assistent erfolgreich erstellt!",
    "assistant_updated": "Assistent erfolgreich aktualisiert!",
    "assistant_deleted": "Assistent erfolgreich gelöscht!",
    "conversation_created": "Konversation erfolgreich erstellt!",
    "message_sent": "Nachricht erfolgreich gesendet!",
    "file_uploaded": "Datei erfolgreich hochgeladen!",
    "document_processed": "Dokument erfolgreich verarbeitet!",
}

# UI Configuration
UI_CONFIG = {
    "sidebar_width": 280,
    "header_height": 70,
    "card_padding": 24,
    "border_radius": 12,
    "transition_duration": 0.3,
}

# Colors
COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    "gray": {
        "50": "#f9fafb",
        "100": "#f3f4f6",
        "200": "#e5e7eb",
        "300": "#d1d5db",
        "400": "#9ca3af",
        "500": "#6b7280",
        "600": "#4b5563",
        "700": "#374151",
        "800": "#1f2937",
        "900": "#111827",
    },
}

# Local Storage Keys
STORAGE_KEYS = {
    "auth_token": "auth_token",
    "user_data": "user_data",
    "language": "language",
    "theme": "theme",
    "sidebar_collapsed": "sidebar_collapsed",
    "recent_conversations": "recent_conversations",
    "user_preferences": "user_preferences",
}

# WebSocket Configuration
WEBSOCKET_CONFIG = {
    "reconnect_attempts": 5,
    "reconnect_delay": 1.0,
    "heartbeat_interval": 30,
    "connection_timeout": 10,
}

# Search Configuration
SEARCH_CONFIG = {
    "min_query_length": 2,
    "max_results": 10,
    "search_delay": 300,  # ms
    "highlight_length": 100,
}

SUPPORTED_AVATAR_TYPES = [
    "image/png",
    "image/jpeg",
    "image/svg+xml",
    "image/webp",
]
