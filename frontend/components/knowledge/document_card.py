"""
Advanced document card component for the AI Assistant Platform.

This module provides a comprehensive document card component for displaying
documents with status indicators, metadata, and various actions.
"""

from collections.abc import Callable

from nicegui import ui
from services.knowledge_service import Document, DocumentStatus, DocumentType
from utils.helpers import format_file_size, format_relative_time


class DocumentCard:
    """Advanced document card component."""

    def __init__(
        self,
        document: Document,
        on_edit: Callable[[Document], None] | None = None,
        on_delete: Callable[[Document], None] | None = None,
        on_download: Callable[[Document], None] | None = None,
        on_reprocess: Callable[[Document], None] | None = None,
        on_view_chunks: Callable[[Document], None] | None = None,
    ):
        """
        Initialize document card.

        Args:
            document: Document to display
            on_edit: Edit callback
            on_delete: Delete callback
            on_download: Download callback
            on_reprocess: Reprocess callback
            on_view_chunks: View chunks callback
        """
        self.document = document
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_download = on_download
        self.on_reprocess = on_reprocess
        self.on_view_chunks = on_view_chunks

        # UI components
        self.container = None
        self.status_indicator = None
        self.progress_bar = None

        self.create_document_card()

    def create_document_card(self):
        """Create the document card UI."""
        self.container = ui.element("div").classes(
            "bg-white border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow",
        )

        with self.container:
            # Header with status
            self.create_header()

            # Document info
            self.create_document_info()

            # Metadata
            self.create_metadata()

            # Actions
            self.create_actions()

    def create_header(self):
        """Create document header with status."""
        with ui.row().classes("items-center justify-between mb-4"):
            # Document name and type
            with ui.column():
                ui.label(self.document.name).classes("font-semibold text-lg")
                with ui.row().classes("items-center space-x-2"):
                    ui.icon(self.get_file_icon()).classes("w-4 h-4 text-gray-500")
                    ui.label(self.document.file_type.value.upper()).classes(
                        "text-sm text-gray-500",
                    )

            # Status indicator
            self.create_status_indicator()

    def create_status_indicator(self):
        """Create status indicator."""
        status_config = {
            DocumentStatus.UPLOADING: {
                "color": "bg-yellow-100 text-yellow-800",
                "icon": "upload",
                "text": "Wird hochgeladen",
            },
            DocumentStatus.PROCESSING: {
                "color": "bg-blue-100 text-blue-800",
                "icon": "sync",
                "text": "Wird verarbeitet",
            },
            DocumentStatus.COMPLETED: {
                "color": "bg-green-100 text-green-800",
                "icon": "check_circle",
                "text": "Abgeschlossen",
            },
            DocumentStatus.FAILED: {
                "color": "bg-red-100 text-red-800",
                "icon": "error",
                "text": "Fehlgeschlagen",
            },
            DocumentStatus.DELETED: {
                "color": "bg-gray-100 text-gray-800",
                "icon": "delete",
                "text": "Gelöscht",
            },
        }

        config = status_config.get(
            self.document.status, status_config[DocumentStatus.FAILED],
        )

        with ui.column().classes("items-end"):
            with ui.row().classes(
                f"items-center space-x-2 px-3 py-1 rounded-full {config['color']}",
            ):
                ui.icon(config["icon"]).classes("w-4 h-4")
                ui.label(config["text"]).classes("text-xs font-medium")

            # Progress bar for processing documents
            if self.document.status in [
                DocumentStatus.UPLOADING,
                DocumentStatus.PROCESSING,
            ]:
                self.progress_bar = ui.linear_progress().classes("w-24 mt-2")
                self.progress_bar.value = 0.5  # This would be updated from the service

    def create_document_info(self):
        """Create document information section."""
        with ui.column().classes("space-y-2 mb-4"):
            # File size and upload date
            with ui.row().classes("items-center justify-between text-sm text-gray-600"):
                ui.label(f"Größe: {format_file_size(self.document.file_size)}")
                ui.label(
                    f"Hochgeladen: {format_relative_time(self.document.uploaded_at)}",
                )

            # Processing date if available
            if self.document.processed_at:
                with ui.row().classes(
                    "items-center justify-between text-sm text-gray-600",
                ):
                    ui.label("Verarbeitet:")
                    ui.label(format_relative_time(self.document.processed_at))

            # Description if available
            if self.document.description:
                ui.label(self.document.description).classes(
                    "text-sm text-gray-700 mt-2",
                )

    def create_metadata(self):
        """Create metadata section."""
        has_metadata = (
            self.document.category
            or self.document.tags
            or self.document.chunks
            or self.document.metadata
        )

        if not has_metadata:
            return

        with ui.expansion("Details", icon="info").classes("mb-4"):
            # Category
            if self.document.category:
                with ui.row().classes("items-center space-x-2 mb-2"):
                    ui.label("Kategorie:").classes("font-medium text-sm")
                    ui.label(self.document.category).classes("text-sm")

            # Tags
            if self.document.tags:
                with ui.row().classes("items-center space-x-2 mb-2"):
                    ui.label("Tags:").classes("font-medium text-sm")
                    with ui.row().classes("flex-wrap gap-1"):
                        for tag in self.document.tags:
                            ui.label(tag).classes(
                                "px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs",
                            )

            # Chunks info
            if self.document.chunks:
                with ui.row().classes("items-center space-x-2 mb-2"):
                    ui.label("Chunks:").classes("font-medium text-sm")
                    ui.label(str(len(self.document.chunks))).classes("text-sm")

            # Version
            if self.document.version:
                with ui.row().classes("items-center space-x-2"):
                    ui.label("Version:").classes("font-medium text-sm")
                    ui.label(self.document.version).classes("text-sm")

            # Custom metadata
            if self.document.metadata:
                with ui.expansion("Zusätzliche Metadaten", icon="settings"):
                    for key, value in self.document.metadata.items():
                        with ui.row().classes("items-start space-x-2"):
                            ui.label(f"{key}:").classes("font-medium text-sm min-w-24")
                            ui.label(str(value)).classes("text-sm flex-1")

    def create_actions(self):
        """Create action buttons."""
        with ui.row().classes("space-x-2"):
            # Download button
            if self.document.status == DocumentStatus.COMPLETED:
                ui.button(
                    "Herunterladen",
                    icon="download",
                    on_click=lambda: self.handle_download(),
                ).classes("bg-blue-500 text-white text-xs")

            # View chunks button
            if self.document.chunks:
                ui.button(
                    "Chunks anzeigen",
                    icon="list",
                    on_click=lambda: self.handle_view_chunks(),
                ).classes("bg-green-500 text-white text-xs")

            # Reprocess button
            if self.document.status in [
                DocumentStatus.COMPLETED,
                DocumentStatus.FAILED,
            ]:
                ui.button(
                    "Neu verarbeiten",
                    icon="refresh",
                    on_click=lambda: self.handle_reprocess(),
                ).classes("bg-orange-500 text-white text-xs")

            # Edit button
            ui.button(
                "Bearbeiten",
                icon="edit",
                on_click=lambda: self.handle_edit(),
            ).classes("bg-gray-500 text-white text-xs")

            # Delete button
            ui.button(
                "Löschen",
                icon="delete",
                on_click=lambda: self.handle_delete(),
            ).classes("bg-red-500 text-white text-xs")

    def get_file_icon(self) -> str:
        """Get appropriate icon for file type."""
        icon_map = {
            DocumentType.PDF: "picture_as_pdf",
            DocumentType.DOCX: "description",
            DocumentType.TXT: "article",
            DocumentType.MD: "code",
            DocumentType.HTML: "code",
            DocumentType.JSON: "data_object",
            DocumentType.CSV: "table_chart",
            DocumentType.IMAGE: "image",
            DocumentType.AUDIO: "audiotrack",
            DocumentType.VIDEO: "video_file",
        }

        return icon_map.get(self.document.file_type, "insert_drive_file")

    def handle_edit(self):
        """Handle edit action."""
        if self.on_edit:
            self.on_edit(self.document)

    def handle_delete(self):
        """Handle delete action."""
        if self.on_delete:
            self.on_delete(self.document)

    def handle_download(self):
        """Handle download action."""
        if self.on_download:
            self.on_download(self.document)

    def handle_reprocess(self):
        """Handle reprocess action."""
        if self.on_reprocess:
            self.on_reprocess(self.document)

    def handle_view_chunks(self):
        """Handle view chunks action."""
        if self.on_view_chunks:
            self.on_view_chunks(self.document)

    def update_progress(self, progress: float):
        """Update progress bar."""
        if self.progress_bar:
            self.progress_bar.value = max(0.0, min(1.0, progress))

    def update_status(self, status: DocumentStatus):
        """Update document status."""
        self.document.status = status
        # Recreate status indicator
        if self.status_indicator:
            self.status_indicator.clear()
            self.create_status_indicator()


def create_document_card(
    document: Document,
    on_edit: Callable[[Document], None] | None = None,
    on_delete: Callable[[Document], None] | None = None,
    on_download: Callable[[Document], None] | None = None,
    on_reprocess: Callable[[Document], None] | None = None,
    on_view_chunks: Callable[[Document], None] | None = None,
) -> DocumentCard:
    """
    Create a document card component.

    Args:
        document: Document to display
        on_edit: Edit callback
        on_delete: Delete callback
        on_download: Download callback
        on_reprocess: Reprocess callback
        on_view_chunks: View chunks callback

    Returns:
        DocumentCard instance
    """
    return DocumentCard(
        document=document,
        on_edit=on_edit,
        on_delete=on_delete,
        on_download=on_download,
        on_reprocess=on_reprocess,
        on_view_chunks=on_view_chunks,
    )
