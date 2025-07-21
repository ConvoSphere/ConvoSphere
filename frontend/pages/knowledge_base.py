"""
Advanced Knowledge Base Page for the AI Assistant Platform.

This module provides comprehensive knowledge base functionality including
document management, search, processing, and embedding integration.
"""

from components.common.error_message import create_error_message
from nicegui import ui
from services.file_service import file_service
from services.knowledge_service import (
    Document,
    DocumentStatus,
    DocumentType,
    SearchResult,
    knowledge_service,
)
from utils.helpers import format_file_size, format_timestamp


class AdvancedKnowledgeBasePage:
    """Advanced knowledge base management page component."""

    def __init__(self):
        """Initialize the advanced knowledge base page."""
        self.documents: list[Document] = []
        self.search_results: list[SearchResult] = []
        self.is_loading = False
        self.is_searching = False
        self.error_message = None
        self.selected_category = "all"
        self.selected_status = "all"
        self.search_query = ""

        # UI components
        self.container = None
        self.documents_container = None
        self.stats_container = None
        self.search_container = None
        self.upload_dialog = None
        self.search_dialog = None

        self.create_knowledge_base_page()
        # Nach dem UI-Aufbau Dokumente laden
        ui.timer(0.1, self.load_documents, once=True)

    def create_knowledge_base_page(self):
        """Create the advanced knowledge base page UI."""
        self.container = ui.element("div").classes("p-6")

        with self.container:
            # Header
            self.create_header()

            # Statistics
            self.create_statistics()

            # Search and filters
            self.create_search_and_filters()

            # Documents list
            self.create_documents_list()

            # Dialogs
            self.upload_dialog = self.create_upload_dialog_ui()
            self.search_dialog = self.create_search_dialog_ui()

    def create_header(self):
        """Create the page header."""
        with ui.element("div").classes("mb-6"):
            with ui.row().classes("items-center justify-between"):
                with ui.column():
                    ui.label("Knowledge Base").classes("text-2xl font-bold")
                    ui.label("Verwalte und durchsuche deine Dokumente").classes(
                        "text-gray-600",
                    )

                with ui.row().classes("space-x-2"):
                    ui.button(
                        "Durchsuchen",
                        icon="search",
                        on_click=self.show_search_dialog,
                    ).classes("bg-green-600 text-white")

                    ui.button(
                        "Dokument hochladen",
                        icon="upload",
                        on_click=self.show_upload_dialog,
                    ).classes("bg-blue-600 text-white")

    def create_statistics(self):
        """Create document statistics display."""
        self.stats_container = ui.element("div").classes("mb-6")

        with self.stats_container:
            with ui.row().classes("grid grid-cols-1 md:grid-cols-4 gap-4"):
                # Total documents
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Gesamt").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-blue-600")

                # Completed documents
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Verarbeitet").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-green-600")

                # Processing documents
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("In Verarbeitung").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-2xl font-bold text-orange-600")

                # Total size
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Gesamtgröße").classes("text-sm text-gray-600")
                    ui.label("0 MB").classes("text-2xl font-bold text-purple-600")

    def create_search_and_filters(self):
        """Create search and filters section."""
        with ui.element("div").classes("mb-6 bg-white border rounded-lg p-4"):
            with ui.row().classes("items-center space-x-4"):
                # Search
                self.search_input = ui.input(
                    placeholder="Dokumente durchsuchen...",
                    on_change=self.handle_search,
                ).classes("flex-1")

                # Category filter
                self.category_select = ui.select(
                    options=["all"] + knowledge_service.get_document_categories(),
                    value="all",
                    label="Kategorie",
                    on_change=self.handle_category_filter,
                ).classes("w-48")

                # Status filter
                self.status_select = ui.select(
                    options=["all"] + [s.value for s in DocumentStatus],
                    value="all",
                    label="Status",
                    on_change=self.handle_status_filter,
                ).classes("w-48")

                # Refresh button
                ui.button(
                    icon="refresh",
                    on_click=self.load_documents,
                ).classes("w-10 h-10 bg-gray-100 text-gray-600")

    def create_documents_list(self):
        """Create the documents list display."""
        self.documents_container = ui.element("div").classes(
            "grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6",
        )

    def create_upload_dialog_ui(self):
        """Create the advanced document upload dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label("Dokument hochladen").classes("text-lg font-medium mb-4")

            # Upload form
            with ui.column().classes("space-y-4"):
                # File upload
                self.file_upload = ui.upload(
                    label="Datei auswählen",
                    multiple=False,
                    on_upload=self.handle_file_upload,
                ).props(
                    "accept=.pdf,.docx,.txt,.md,.html,.json,.csv,.jpg,.jpeg,.png,.mp3,.mp4",
                )

                # Document metadata
                with ui.row().classes("space-x-4"):
                    name_input = ui.input("Name *").classes("flex-1")
                    category_input = ui.input("Kategorie").classes("flex-1")

                description_input = ui.textarea("Beschreibung").classes("w-full")
                tags_input = ui.input("Tags (kommagetrennt)").classes("w-full")

                # Processing options
                with ui.expansion("Verarbeitungsoptionen", icon="settings"):
                    with ui.column().classes("space-y-2"):
                        ui.switch("Automatische Kategorisierung").classes("w-full")
                        ui.switch("Tags extrahieren").classes("w-full")
                        ui.switch("Metadaten extrahieren").classes("w-full")

                # Buttons
                with ui.row().classes("justify-end space-x-2"):
                    ui.button(
                        "Abbrechen",
                        on_click=dialog.close,
                    ).classes("bg-gray-500 text-white")

                    ui.button(
                        "Hochladen",
                        on_click=lambda: self.upload_document(
                            name_input.value,
                            description_input.value,
                            category_input.value,
                            tags_input.value,
                            dialog,
                        ),
                    ).classes("bg-blue-600 text-white")

        return dialog

    def create_search_dialog_ui(self):
        """Create the advanced search dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-4xl"):
            ui.label("Dokumente durchsuchen").classes("text-lg font-medium mb-4")

            with ui.column().classes("space-y-4"):
                # Search input
                search_input = ui.input(
                    placeholder="Suchbegriff eingeben...",
                    label="Suche",
                ).classes("w-full")

                # Register keydown event after creation
                search_input.on(
                    "keydown",
                    lambda e: self.perform_search(e, search_input.value, dialog)
                    if e.key == "Enter"
                    else None,
                )

                # Search filters
                with ui.row().classes("space-x-4"):
                    ui.select(
                        options=["alle"] + knowledge_service.get_document_categories(),
                        label="Kategorie",
                    ).classes("flex-1")
                    ui.select(
                        options=["alle"] + [s.value for s in DocumentStatus],
                        label="Status",
                    ).classes("flex-1")
                    ui.number("Max. Ergebnisse", value=20).classes("w-32")

                # Search button
                ui.button(
                    "Suchen",
                    icon="search",
                    on_click=lambda: self.perform_search(
                        None, search_input.value, dialog,
                    ),
                ).classes("bg-green-600 text-white")

                # Results container
                self.search_results_container = ui.element("div").classes("space-y-4")

        return dialog

    async def load_documents(self):
        """Load documents from the API."""
        self.is_loading = True

        try:
            self.documents = await knowledge_service.get_documents(force_refresh=True)
            self.display_documents()
            self.update_statistics()

        except Exception as e:
            self.error_message = f"Fehler beim Laden der Dokumente: {str(e)}"
            self.display_error()
        finally:
            self.is_loading = False

    def display_documents(self):
        """Display documents in the grid."""
        self.documents_container.clear()

        # Apply filters
        filtered_documents = self.filter_documents()

        if not filtered_documents:
            with self.documents_container:
                ui.label("Keine Dokumente gefunden").classes(
                    "col-span-full text-center text-gray-500 py-8",
                )
            return

        with self.documents_container:
            for document in filtered_documents:
                self.create_document_card(document)

    def filter_documents(self) -> list[Document]:
        """Filter documents based on current filters."""
        filtered = self.documents

        # Category filter
        if self.selected_category != "all":
            filtered = [d for d in filtered if d.category == self.selected_category]

        # Status filter
        if self.selected_status != "all":
            filtered = [d for d in filtered if d.status.value == self.selected_status]

        # Search filter
        if self.search_query:
            query_lower = self.search_query.lower()
            filtered = [
                d
                for d in filtered
                if query_lower in d.name.lower()
                or (d.description and query_lower in d.description.lower())
            ]

        return filtered

    def update_statistics(self):
        """Update statistics display."""
        stats = knowledge_service.get_document_stats()

        self.stats_container.clear()
        with self.stats_container:
            with ui.row().classes("grid grid-cols-1 md:grid-cols-4 gap-4"):
                # Total documents
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Gesamt").classes("text-sm text-gray-600")
                    ui.label(str(stats["total_documents"])).classes(
                        "text-2xl font-bold text-blue-600",
                    )

                # Completed documents
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Verarbeitet").classes("text-sm text-gray-600")
                    ui.label(str(stats["completed_documents"])).classes(
                        "text-2xl font-bold text-green-600",
                    )

                # Processing documents
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("In Verarbeitung").classes("text-sm text-gray-600")
                    ui.label(str(stats["processing_documents"])).classes(
                        "text-2xl font-bold text-orange-600",
                    )

                # Total size
                with ui.element("div").classes("bg-white border rounded-lg p-4"):
                    ui.label("Gesamtgröße").classes("text-sm text-gray-600")
                    ui.label(stats["total_size_formatted"]).classes(
                        "text-2xl font-bold text-purple-600",
                    )

    def create_document_card(self, document: Document):
        """Create a document card."""
        with ui.element("div").classes(
            "bg-white border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow",
        ):
            # Header with status
            with ui.row().classes("items-center justify-between mb-4"):
                # Document name and type
                with ui.column():
                    ui.label(document.name).classes("font-semibold text-lg")
                    with ui.row().classes("items-center space-x-2"):
                        ui.icon(self.get_file_icon(document.file_type)).classes(
                            "w-4 h-4 text-gray-500",
                        )
                        ui.label(document.file_type.value.upper()).classes(
                            "text-sm text-gray-500",
                        )

                # Status indicator
                self.create_status_indicator(document.status)

            # Document info
            with ui.column().classes("space-y-2 mb-4"):
                # File size and upload date
                with ui.row().classes(
                    "items-center justify-between text-sm text-gray-600",
                ):
                    ui.label(f"Größe: {format_file_size(document.file_size)}")
                    ui.label(f"Hochgeladen: {format_timestamp(document.uploaded_at)}")

                # Processing date if available
                if document.processed_at:
                    with ui.row().classes(
                        "items-center justify-between text-sm text-gray-600",
                    ):
                        ui.label("Verarbeitet:")
                        ui.label(format_timestamp(document.processed_at))

                # Description if available
                if document.description:
                    ui.label(document.description).classes("text-sm text-gray-700 mt-2")

            # Actions
            with ui.row().classes("space-x-2"):
                # Download button
                if document.status == DocumentStatus.COMPLETED:
                    ui.button(
                        "Herunterladen",
                        icon="download",
                        on_click=lambda: self.download_document(document),
                    ).classes("bg-blue-500 text-white text-xs")

                # View chunks button
                if document.chunks:
                    ui.button(
                        "Chunks anzeigen",
                        icon="list",
                        on_click=lambda: self.view_document_chunks(document),
                    ).classes("bg-green-500 text-white text-xs")

                # Reprocess button
                if document.status in [DocumentStatus.COMPLETED, DocumentStatus.FAILED]:
                    ui.button(
                        "Neu verarbeiten",
                        icon="refresh",
                        on_click=lambda: self.reprocess_document(document),
                    ).classes("bg-orange-500 text-white text-xs")

                # Edit button
                ui.button(
                    "Bearbeiten",
                    icon="edit",
                    on_click=lambda: self.edit_document(document),
                ).classes("bg-gray-500 text-white text-xs")

                # Delete button
                ui.button(
                    "Löschen",
                    icon="delete",
                    on_click=lambda: self.delete_document(document),
                ).classes("bg-red-500 text-white text-xs")

    def create_status_indicator(self, status: DocumentStatus):
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

        config = status_config.get(status, status_config[DocumentStatus.FAILED])

        with ui.column().classes("items-end"):
            with ui.row().classes(
                f"items-center space-x-2 px-3 py-1 rounded-full {config['color']}",
            ):
                ui.icon(config["icon"]).classes("w-4 h-4")
                ui.label(config["text"]).classes("text-xs font-medium")

    def get_file_icon(self, doc_type: DocumentType) -> str:
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

        return icon_map.get(doc_type, "insert_drive_file")

    def display_error(self):
        """Display error message."""
        self.documents_container.clear()
        with self.documents_container:
            create_error_message(self.error_message)

    def handle_search(self, event):
        """Handle search input change."""
        self.search_query = event.value
        self.display_documents()

    def handle_category_filter(self, event):
        """Handle category filter change."""
        self.selected_category = event.value
        self.display_documents()

    def handle_status_filter(self, event):
        """Handle status filter change."""
        self.selected_status = event.value
        self.display_documents()

    def show_upload_dialog(self):
        """Show the upload dialog."""
        self.upload_dialog.open()

    def show_search_dialog(self):
        """Show the search dialog."""
        self.search_dialog.open()

    async def handle_file_upload(self, event):
        """Handle file upload using file service."""
        if not event.files:
            return

        file = event.files[0]  # Single file upload

        # Validate file using file service
        validation = file_service.validate_file(file.content, file.name, file.type)
        if not validation["valid"]:
            error_msg = "; ".join(validation["errors"])
            ui.notify(f"Datei {file.name}: {error_msg}", type="error")
            return

        # Store file info for upload
        self.upload_file_info = {
            "name": file.name,
            "type": file.type,
            "size": file.size,
            "data": file.content,
            "file_id": None,
            "upload_progress": 0.0,
        }

        ui.notify(f"Datei {file.name} validiert, bereit zum Hochladen", type="info")

    async def upload_document(
        self,
        name: str,
        description: str,
        category: str,
        tags: str,
        dialog,
    ):
        """Upload a document using file service."""
        try:
            # Validate input
            if not name:
                ui.notify("Name ist erforderlich", type="error")
                return

            if not hasattr(self, "upload_file_info") or not self.upload_file_info:
                ui.notify("Bitte wählen Sie zuerst eine Datei aus", type="error")
                return

            # Parse tags
            tag_list = (
                [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
            )

            # Prepare metadata
            metadata = {
                "name": name,
                "description": description,
                "category": category,
                "tags": tag_list,
                "document_type": "knowledge_base",
            }

            # Upload file using file service
            file_id = await file_service.upload_file(
                file_data=self.upload_file_info["data"],
                filename=self.upload_file_info["name"],
                mime_type=self.upload_file_info["type"],
                endpoint="/api/v1/knowledge/upload",
                metadata=metadata,
                on_progress=self.update_upload_progress,
                on_complete=self.on_upload_complete,
                on_error=self.on_upload_error,
            )

            if file_id:
                ui.notify("Dokument wird hochgeladen...", type="info")
                # The dialog will be closed in on_upload_complete
            else:
                ui.notify("Fehler beim Hochladen des Dokuments", type="error")

        except Exception as e:
            ui.notify(f"Fehler beim Hochladen des Dokuments: {str(e)}", type="error")

    def update_upload_progress(self, progress):
        """Update upload progress."""
        if hasattr(self, "upload_file_info"):
            self.upload_file_info["upload_progress"] = progress.percentage
            ui.notify(f"Upload: {progress.percentage:.1f}%", type="info")

    def on_upload_complete(self, result):
        """Handle upload completion."""
        file_id = result.get("file_id")
        filename = result.get("filename")

        ui.notify(f"Dokument {filename} erfolgreich hochgeladen", type="positive")

        # Close dialog and refresh documents
        if hasattr(self, "upload_dialog"):
            self.upload_dialog.close()

        # Clear upload file info
        if hasattr(self, "upload_file_info"):
            del self.upload_file_info

        # Refresh documents list
        ui.timer(0.1, self.load_documents, once=True)

    def on_upload_error(self, error_msg):
        """Handle upload error."""
        ui.notify(f"Upload fehlgeschlagen: {error_msg}", type="error")

    async def perform_search(self, event, query: str, dialog):
        """Perform document search."""
        if not query.strip():
            return

        self.is_searching = True

        try:
            results = await knowledge_service.search_documents(query)

            # Display results
            self.search_results_container.clear()

            if results:
                with self.search_results_container:
                    for result in results:
                        self.create_search_result_item(result)
            else:
                with self.search_results_container:
                    ui.label("Keine Ergebnisse gefunden").classes(
                        "text-gray-500 text-center py-4",
                    )

        except Exception as e:
            ui.notify(f"Fehler bei der Suche: {str(e)}", type="error")
        finally:
            self.is_searching = False

    def create_search_result_item(self, result: SearchResult):
        """Create a search result item."""
        with ui.element("div").classes("border rounded p-4 bg-gray-50"):
            with ui.row().classes("items-center justify-between mb-2"):
                ui.label(result.document_name).classes("font-medium")
                ui.label(f"Score: {result.score:.2f}").classes("text-sm text-gray-600")

            # Highlighted content
            content = (
                result.content[:200] + "..."
                if len(result.content) > 200
                else result.content
            )
            ui.label(content).classes("text-sm text-gray-700 mb-2")

            # Metadata
            with ui.row().classes("items-center justify-between text-xs text-gray-500"):
                ui.label(f"Chunk {result.chunk_index}")
                ui.label(f"Position {result.start_position}-{result.end_position}")

    async def edit_document(self, document: Document):
        """Edit a document."""
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg"):
            ui.label(f"Dokument bearbeiten: {document.name}").classes(
                "text-lg font-medium mb-4",
            )

            with ui.column().classes("space-y-4"):
                name_input = ui.input("Name", value=document.name).classes("w-full")
                description_input = ui.textarea(
                    "Beschreibung", value=document.description or "",
                ).classes("w-full")
                category_input = ui.input(
                    "Kategorie", value=document.category or "",
                ).classes("w-full")
                tags_input = ui.input(
                    "Tags", value=", ".join(document.tags or []),
                ).classes("w-full")

                with ui.row().classes("justify-end space-x-2"):
                    ui.button("Abbrechen", on_click=dialog.close).classes(
                        "bg-gray-500 text-white",
                    )
                    ui.button(
                        "Speichern",
                        on_click=lambda: self.save_document_edit(
                            document.id,
                            name_input.value,
                            description_input.value,
                            category_input.value,
                            tags_input.value,
                            dialog,
                        ),
                    ).classes("bg-blue-600 text-white")

    async def save_document_edit(
        self,
        document_id: str,
        name: str,
        description: str,
        category: str,
        tags: str,
        dialog,
    ):
        """Save document edit."""
        try:
            tag_list = (
                [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
            )

            document_data = {
                "name": name,
                "description": description,
                "category": category,
                "tags": tag_list,
            }

            document = await knowledge_service.update_document(
                document_id, document_data,
            )

            if document:
                ui.notify("Dokument erfolgreich aktualisiert", type="positive")
                dialog.close()
                await self.load_documents()
            else:
                ui.notify("Fehler beim Aktualisieren des Dokuments", type="error")

        except Exception as e:
            ui.notify(f"Fehler beim Aktualisieren: {str(e)}", type="error")

    async def delete_document(self, document: Document):
        """Delete a document."""
        try:
            success = await knowledge_service.delete_document(document.id)

            if success:
                ui.notify("Dokument erfolgreich gelöscht", type="positive")
                await self.load_documents()
            else:
                ui.notify("Fehler beim Löschen des Dokuments", type="error")

        except Exception as e:
            ui.notify(f"Fehler beim Löschen des Dokuments: {str(e)}", type="error")

    async def download_document(self, document: Document):
        """Download a document."""
        ui.notify("Download-Funktionalität wird implementiert", type="info")

    async def reprocess_document(self, document: Document):
        """Reprocess a document."""
        try:
            success = await knowledge_service.reprocess_document(document.id)

            if success:
                ui.notify("Dokument wird neu verarbeitet", type="positive")
                await self.load_documents()
            else:
                ui.notify("Fehler bei der Neuverarbeitung", type="error")

        except Exception as e:
            ui.notify(f"Fehler bei der Neuverarbeitung: {str(e)}", type="error")

    async def view_document_chunks(self, document: Document):
        """View document chunks."""
        try:
            chunks = await knowledge_service.get_document_chunks(document.id)

            with ui.dialog() as dialog, ui.card().classes("w-full max-w-4xl"):
                ui.label(f"Chunks: {document.name}").classes("text-lg font-medium mb-4")

                with ui.column().classes("space-y-4 max-h-96 overflow-y-auto"):
                    for chunk in chunks:
                        with ui.element("div").classes("border rounded p-3 bg-gray-50"):
                            with ui.row().classes("items-center justify-between mb-2"):
                                ui.label(f"Chunk {chunk.chunk_index}").classes(
                                    "font-medium",
                                )
                                ui.label(
                                    f"Position {chunk.start_position}-{chunk.end_position}",
                                ).classes("text-sm text-gray-600")

                            ui.label(chunk.content).classes("text-sm")

                ui.button("Schließen", on_click=dialog.close).classes(
                    "bg-blue-600 text-white",
                )

        except Exception as e:
            ui.notify(f"Fehler beim Laden der Chunks: {str(e)}", type="error")


def create_page():
    """Create and return a knowledge base page instance."""
    return AdvancedKnowledgeBasePage()
