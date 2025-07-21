"""
Advanced upload component for the AI Assistant Platform.

This module provides comprehensive file upload functionality for the knowledge base
including drag-and-drop, progress tracking, and batch upload support.
"""

import asyncio
from collections.abc import Callable
from datetime import datetime
from typing import Any

from nicegui import ui
from services.knowledge_service import Document, DocumentStatus, DocumentType
from utils.helpers import format_file_size
from utils.validators import validate_document_data


class AdvancedUploadComponent:
    """Advanced upload component for knowledge base."""

    def __init__(
        self,
        on_upload: Callable[[list[dict[str, Any]]], None] | None = None,
        on_progress: Callable[[str, float], None] | None = None,
        on_complete: Callable[[list[Document]], None] | None = None,
    ):
        """
        Initialize upload component.

        Args:
            on_upload: Upload callback function
            on_progress: Progress callback function
            on_complete: Complete callback function
        """
        self.on_upload = on_upload
        self.on_progress = on_progress
        self.on_complete = on_complete

        # Upload state
        self.upload_queue: list[dict[str, Any]] = []
        self.uploading_files: dict[str, dict[str, Any]] = {}
        self.completed_uploads: list[Document] = []
        self.failed_uploads: list[dict[str, Any]] = []
        self.is_uploading = False

        # UI components
        self.container = None
        self.drop_zone = None
        self.file_list = None
        self.progress_container = None

        self.create_upload_component()

    def create_upload_component(self):
        """Create the upload component UI."""
        self.container = ui.element("div").classes("w-full")

        with self.container:
            # Drop zone
            self.create_drop_zone()

            # File list
            self.create_file_list()

            # Progress section
            self.create_progress_section()

            # Upload controls
            self.create_upload_controls()

    def create_drop_zone(self):
        """Create drag-and-drop zone."""
        self.drop_zone = ui.element("div").classes(
            "border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors",
        )

        with self.drop_zone:
            ui.icon("cloud_upload").classes("w-12 h-12 text-gray-400 mx-auto mb-4")
            ui.label("Dateien hier hineinziehen oder klicken zum Auswählen").classes(
                "text-lg text-gray-600 mb-2",
            )
            ui.label(
                "Unterstützte Formate: PDF, DOCX, TXT, MD, HTML, JSON, CSV, Bilder, Audio, Video",
            ).classes("text-sm text-gray-500")

            # File input
            self.file_input = ui.upload(
                label="Dateien auswählen",
                multiple=True,
                on_upload=self.handle_file_select,
            ).props(
                "accept=.pdf,.docx,.txt,.md,.html,.json,.csv,.jpg,.jpeg,.png,.gif,.mp3,.mp4,.avi,.mov",
            )

    def create_file_list(self):
        """Create file list display."""
        with ui.element("div").classes("mt-6"):
            ui.label("Ausgewählte Dateien").classes("text-lg font-medium mb-4")
            self.file_list = ui.element("div").classes("space-y-2")

    def create_progress_section(self):
        """Create upload progress section."""
        with ui.element("div").classes("mt-6"):
            ui.label("Upload-Fortschritt").classes("text-lg font-medium mb-4")
            self.progress_container = ui.element("div").classes("space-y-4")

    def create_upload_controls(self):
        """Create upload control buttons."""
        with ui.element("div").classes("mt-6 flex justify-between items-center"):
            with ui.row().classes("space-x-2"):
                ui.button(
                    "Alle hochladen",
                    icon="upload",
                    on_click=self.start_batch_upload,
                ).classes("bg-blue-600 text-white")

                ui.button(
                    "Liste löschen",
                    icon="clear",
                    on_click=self.clear_upload_queue,
                ).classes("bg-gray-500 text-white")

            with ui.row().classes("space-x-2"):
                ui.button(
                    "Erweiterte Optionen",
                    icon="settings",
                    on_click=self.show_advanced_options,
                ).classes("bg-green-600 text-white")

    def handle_file_select(self, event):
        """Handle file selection."""
        files = event.files if hasattr(event, "files") else [event]

        for file in files:
            file_info = {
                "name": file.name,
                "size": len(file.content) if hasattr(file, "content") else 0,
                "type": file.type if hasattr(file, "type") else "unknown",
                "content": file.content if hasattr(file, "content") else b"",
                "status": "pending",
                "progress": 0.0,
                "error": None,
            }

            # Validate file
            if not self.validate_file(file_info):
                file_info["status"] = "error"
                file_info["error"] = "Ungültiger Dateityp oder zu große Datei"

            self.upload_queue.append(file_info)

        self.update_file_list()

    def validate_file(self, file_info: dict[str, Any]) -> bool:
        """Validate file for upload."""
        # Check file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        if file_info["size"] > max_size:
            return False

        # Check file type
        supported_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "text/markdown",
            "text/html",
            "application/json",
            "text/csv",
            "image/jpeg",
            "image/png",
            "image/gif",
            "audio/mpeg",
            "video/mp4",
            "video/avi",
            "video/quicktime",
        ]

        return file_info["type"] in supported_types

    def update_file_list(self):
        """Update file list display."""
        self.file_list.clear()

        if not self.upload_queue:
            with self.file_list:
                ui.label("Keine Dateien ausgewählt").classes(
                    "text-gray-500 text-center py-4",
                )
            return

        with self.file_list:
            for i, file_info in enumerate(self.upload_queue):
                self.create_file_item(file_info, i)

    def create_file_item(self, file_info: dict[str, Any], index: int):
        """Create a file item in the list."""
        with ui.element("div").classes("bg-white border rounded-lg p-4"):
            with ui.row().classes("items-center justify-between"):
                # File info
                with ui.column():
                    ui.label(file_info["name"]).classes("font-medium")
                    ui.label(
                        f"{format_file_size(file_info['size'])} • {file_info['type']}",
                    ).classes("text-sm text-gray-600")

                # Status and actions
                with ui.row().classes("items-center space-x-2"):
                    # Status indicator
                    status_color = {
                        "pending": "text-gray-500",
                        "uploading": "text-blue-500",
                        "completed": "text-green-500",
                        "error": "text-red-500",
                    }.get(file_info["status"], "text-gray-500")

                    status_icon = {
                        "pending": "schedule",
                        "uploading": "sync",
                        "completed": "check_circle",
                        "error": "error",
                    }.get(file_info["status"], "help")

                    ui.icon(status_icon).classes(f"w-5 h-5 {status_color}")

                    # Progress bar for uploading files
                    if file_info["status"] == "uploading":
                        progress_bar = ui.linear_progress().classes("w-24")
                        progress_bar.value = file_info["progress"]

                    # Error message
                    if file_info["error"]:
                        ui.label(file_info["error"]).classes("text-xs text-red-500")

                    # Remove button
                    ui.button(
                        icon="delete",
                        on_click=lambda idx=index: self.remove_file(idx),
                    ).classes("bg-red-500 text-white text-xs")

    def remove_file(self, index: int):
        """Remove file from upload queue."""
        if 0 <= index < len(self.upload_queue):
            del self.upload_queue[index]
            self.update_file_list()

    def clear_upload_queue(self):
        """Clear all files from upload queue."""
        self.upload_queue.clear()
        self.update_file_list()

    async def start_batch_upload(self):
        """Start batch upload of all files."""
        if not self.upload_queue:
            ui.notify("Keine Dateien zum Hochladen", type="warning")
            return

        if self.is_uploading:
            ui.notify("Upload läuft bereits", type="warning")
            return

        self.is_uploading = True
        self.completed_uploads = []
        self.failed_uploads = []

        # Update progress section
        self.progress_container.clear()

        with self.progress_container:
            # Overall progress
            self.overall_progress = ui.linear_progress().classes("w-full mb-4")
            self.overall_progress.value = 0.0

            # Progress label
            self.progress_label = ui.label("Bereite Upload vor...").classes(
                "text-sm text-gray-600",
            )

        try:
            total_files = len(self.upload_queue)
            completed_files = 0

            for i, file_info in enumerate(self.upload_queue):
                if file_info["status"] == "error":
                    continue

                # Update file status
                file_info["status"] = "uploading"
                file_info["progress"] = 0.0
                self.update_file_list()

                # Update progress
                self.progress_label.text = (
                    f"Lade hoch: {file_info['name']} ({i + 1}/{total_files})"
                )

                try:
                    # Simulate upload progress
                    for progress in range(0, 101, 10):
                        file_info["progress"] = progress / 100.0
                        self.update_file_list()
                        await asyncio.sleep(0.1)

                    # Create document data
                    document_data = {
                        "name": file_info["name"],
                        "file_type": file_info["type"],
                        "file_size": file_info["size"],
                        "description": "Uploaded via batch upload",
                        "category": "Upload",
                        "tags": ["batch-upload"],
                    }

                    # Validate document data
                    validation = validate_document_data(document_data)
                    if not validation["valid"]:
                        raise ValueError(
                            f"Document validation failed: {validation['errors']}",
                        )

                    # Call upload callback
                    if self.on_upload:
                        await self.on_upload([document_data])

                    # Mark as completed
                    file_info["status"] = "completed"
                    file_info["progress"] = 1.0
                    completed_files += 1

                    # Create document object for completion callback
                    document = Document(
                        id=f"doc_{i}",
                        name=file_info["name"],
                        filename=file_info["name"],
                        file_type=DocumentType.UNKNOWN,
                        file_size=file_info["size"],
                        status=DocumentStatus.COMPLETED,
                        uploaded_at=datetime.now(),
                    )
                    self.completed_uploads.append(document)

                except Exception as e:
                    file_info["status"] = "error"
                    file_info["error"] = str(e)
                    self.failed_uploads.append(file_info)

                # Update overall progress
                self.overall_progress.value = (i + 1) / total_files
                self.update_file_list()

            # Upload complete
            self.progress_label.text = (
                f"Upload abgeschlossen: {completed_files}/{total_files} erfolgreich"
            )

            # Call completion callback
            if self.on_complete:
                self.on_complete(self.completed_uploads)

            # Show results
            self.show_upload_results()

        except Exception as e:
            ui.notify(f"Fehler beim Upload: {str(e)}", type="error")
        finally:
            self.is_uploading = False

    def show_upload_results(self):
        """Show upload results summary."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg"):
            ui.label("Upload-Ergebnisse").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                # Success count
                if self.completed_uploads:
                    with ui.row().classes("items-center space-x-2"):
                        ui.icon("check_circle").classes("w-5 h-5 text-green-500")
                        ui.label(
                            f"{len(self.completed_uploads)} Dateien erfolgreich hochgeladen",
                        ).classes("text-green-600")

                # Error count
                if self.failed_uploads:
                    with ui.row().classes("items-center space-x-2"):
                        ui.icon("error").classes("w-5 h-5 text-red-500")
                        ui.label(
                            f"{len(self.failed_uploads)} Dateien fehlgeschlagen",
                        ).classes("text-red-600")

                # Failed files list
                if self.failed_uploads:
                    with ui.expansion("Fehlgeschlagene Dateien", icon="error"):
                        for file_info in self.failed_uploads:
                            with ui.row().classes("items-center space-x-2"):
                                ui.label(file_info["name"]).classes("text-sm")
                                ui.label(file_info["error"]).classes(
                                    "text-xs text-red-500",
                                )

            ui.button("Schließen", on_click=dialog.close).classes(
                "bg-blue-600 text-white",
            )

    def show_advanced_options(self):
        """Show advanced upload options dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg"):
            ui.label("Erweiterte Upload-Optionen").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                # Processing options
                with ui.expansion("Verarbeitungsoptionen", icon="settings"):
                    ui.switch("Automatische Kategorisierung").classes("w-full")
                    ui.switch("Tags extrahieren").classes("w-full")
                    ui.switch("Metadaten extrahieren").classes("w-full")
                    ui.switch("OCR für Bilder").classes("w-full")

                # Chunking options
                with ui.expansion("Chunking-Optionen", icon="content_cut"):
                    ui.number("Chunk-Größe", value=500, min=100, max=2000).classes(
                        "w-full",
                    )
                    ui.number("Chunk-Überlappung", value=50, min=0, max=200).classes(
                        "w-full",
                    )

                # Embedding options
                with ui.expansion("Embedding-Optionen", icon="memory"):
                    ui.select(
                        "Embedding-Modell",
                        options=["text-embedding-ada-002", "text-embedding-3-small"],
                    ).classes("w-full")
                    ui.switch("Automatische Embedding-Generierung").classes("w-full")

            with ui.row().classes("justify-end space-x-2"):
                ui.button("Abbrechen", on_click=dialog.close).classes(
                    "bg-gray-500 text-white",
                )
                ui.button("Speichern", on_click=dialog.close).classes(
                    "bg-blue-600 text-white",
                )

    def get_upload_queue(self) -> list[dict[str, Any]]:
        """Get current upload queue."""
        return self.upload_queue.copy()

    def get_completed_uploads(self) -> list[Document]:
        """Get completed uploads."""
        return self.completed_uploads.copy()

    def get_failed_uploads(self) -> list[dict[str, Any]]:
        """Get failed uploads."""
        return self.failed_uploads.copy()

    def is_upload_in_progress(self) -> bool:
        """Check if upload is in progress."""
        return self.is_uploading


def create_advanced_upload_component(
    on_upload: Callable[[list[dict[str, Any]]], None] | None = None,
    on_progress: Callable[[str, float], None] | None = None,
    on_complete: Callable[[list[Document]], None] | None = None,
) -> AdvancedUploadComponent:
    """
    Create an advanced upload component.

    Args:
        on_upload: Upload callback function
        on_progress: Progress callback function
        on_complete: Complete callback function

    Returns:
        AdvancedUploadComponent instance
    """
    return AdvancedUploadComponent(
        on_upload=on_upload,
        on_progress=on_progress,
        on_complete=on_complete,
    )
