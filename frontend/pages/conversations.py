"""
Conversations page for the AI Assistant Platform.

This module provides comprehensive conversation management with
real-time updates, search, filtering, and conversation history.
"""

from typing import Any

from components.common.error_message import ErrorSeverity, create_error_message
from components.common.loading_spinner import create_loading_spinner
from nicegui import ui
from services.assistant_service import assistant_service
from services.conversation_service import conversation_service
from services.error_handler import handle_network_error
from services.websocket_service import websocket_service
from utils.helpers import format_relative_time


class ConversationsPage:
    """Conversations management page with real-time updates."""

    def __init__(self):
        """Initialize conversations page."""
        self.conversations = []
        self.assistants = []
        self.is_loading = False
        self.search_query = ""
        self.selected_assistant_filter = "all"
        self.selected_status_filter = "all"

        # UI Components
        self.conversations_container = None
        self.search_input = None
        self.filters_container = None
        self.loading_spinner = None
        self.error_component = None
        self.create_conversation_dialog = None

        # WebSocket connection for real-time updates
        self.websocket_connected = False

        self.create_conversations_interface()
        self.initialize_conversations()

    def create_conversations_interface(self):
        """Create the conversations interface UI."""
        with ui.column().classes("h-screen flex flex-col"):
            # Header
            self.create_page_header()

            # Search and Filters
            self.create_search_and_filters()

            # Conversations List
            with ui.element("div").classes("flex-1 overflow-hidden"):
                self.conversations_container = ui.element("div").classes(
                    "h-full overflow-y-auto p-4 space-y-4",
                )

            # Loading and Error States
            self.loading_spinner = create_loading_spinner(
                "Lade Konversationen...", size="lg",
            )
            self.error_component = create_error_message("", dismissible=True)

    def create_page_header(self):
        """Create the page header."""
        with ui.element("div").classes(
            "flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800",
        ):
            with ui.element("div").classes("flex items-center space-x-3"):
                ui.icon("chat").classes("h-6 w-6 text-blue-600 dark:text-blue-400")
                with ui.element("div"):
                    ui.html(
                        "<h1 style='font-size: 24px; font-weight: 700; color: var(--color-text);'>Konversationen</h1>",
                    )
                    ui.html(
                        "<p style='font-size: 14px; color: var(--color-text-secondary);'>Chat-Verlauf und Nachrichten</p>",
                    )

            # Create new conversation button
            ui.button(
                "Neue Konversation",
                icon="add",
                on_click=self.show_create_conversation_dialog,
            ).classes("bg-blue-600 text-white")

    def create_search_and_filters(self):
        """Create search and filters section."""
        with ui.element("div").classes(
            "p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800",
        ):
            with ui.element("div").classes("flex flex-col space-y-4"):
                # Search input
                self.search_input = ui.input(
                    placeholder="Konversationen durchsuchen...",
                    on_change=self.handle_search_change,
                ).classes("w-full")

                # Filters
                with ui.element("div").classes("flex space-x-4"):
                    # Assistant filter
                    ui.select(
                        "Assistent",
                        options=["alle"]
                        + [assistant.get("name", "") for assistant in self.assistants],
                        value="alle",
                        on_change=self.handle_assistant_filter_change,
                    ).classes("w-48")

                    # Status filter
                    ui.select(
                        "Status",
                        options=["alle", "aktiv", "archiviert"],
                        value="alle",
                        on_change=self.handle_status_filter_change,
                    ).classes("w-48")

                    # Clear filters
                    ui.button(
                        "Filter löschen",
                        icon="clear",
                        on_click=self.clear_filters,
                    ).classes("bg-gray-500 text-white")

    async def initialize_conversations(self):
        """Initialize conversations data."""
        self.is_loading = True
        self.loading_spinner.show()
        self.error_component.hide()

        try:
            # Load assistants for filter
            self.assistants = await assistant_service.get_assistants()

            # Load conversations
            await self.load_conversations()

            # Connect to WebSocket for real-time updates
            await self.connect_websocket()

        except Exception as e:
            handle_network_error(e, "Initialisierung der Konversationen")
            self.error_component.update_message(
                f"Fehler beim Laden der Konversationen: {str(e)}",
                ErrorSeverity.ERROR,
            )
            self.error_component.show()

        finally:
            self.is_loading = False
            self.loading_spinner.hide()

    async def load_conversations(self):
        """Load conversations from API."""
        try:
            self.conversations = await conversation_service.get_conversations()
            self.display_conversations()
        except Exception as e:
            handle_network_error(e, "Laden der Konversationen")
            raise

    def display_conversations(self):
        """Display conversations in the UI."""
        if not self.conversations_container:
            return

        self.conversations_container.clear()

        if not self.conversations:
            with self.conversations_container:
                with ui.element("div").classes("text-center py-8"):
                    ui.icon("chat").classes("h-12 w-12 text-gray-400 mx-auto mb-4")
                    ui.html(
                        "<p style='font-size: 16px; color: var(--color-text-secondary);'>Keine Konversationen gefunden</p>",
                    )
                    ui.html(
                        "<p style='font-size: 14px; color: var(--color-text-secondary);'>Erstelle eine neue Konversation um zu beginnen</p>",
                    )
            return

        # Filter conversations
        filtered_conversations = self.filter_conversations()

        with self.conversations_container:
            for conversation in filtered_conversations:
                self.create_conversation_card(conversation)

    def filter_conversations(self) -> list[dict[str, Any]]:
        """Filter conversations based on search and filters."""
        filtered = self.conversations

        # Search filter
        if self.search_query:
            search_lower = self.search_query.lower()
            filtered = [
                conv
                for conv in filtered
                if search_lower in conv.get("title", "").lower()
                or search_lower in conv.get("assistant_name", "").lower()
            ]

        # Assistant filter
        if self.selected_assistant_filter != "alle":
            filtered = [
                conv
                for conv in filtered
                if conv.get("assistant_name") == self.selected_assistant_filter
            ]

        # Status filter
        if self.selected_status_filter != "alle":
            status_map = {"aktiv": True, "archiviert": False}
            target_status = status_map.get(self.selected_status_filter)
            filtered = [
                conv for conv in filtered if conv.get("is_active") == target_status
            ]

        return filtered

    def create_conversation_card(self, conversation: dict[str, Any]):
        """Create a conversation card."""
        with ui.element("div").classes(
            "bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow",
        ):
            with ui.element("div").classes("flex items-center justify-between"):
                # Conversation info
                with ui.element("div").classes("flex-1"):
                    ui.html(
                        f"<h3 style='font-size: 16px; font-weight: 600; color: var(--color-text);'>{conversation.get('title', 'Unbenannte Konversation')}</h3>",
                    )
                    ui.html(
                        f"<p style='font-size: 14px; color: var(--color-text-secondary);'>Assistent: {conversation.get('assistant_name', 'Unbekannt')}</p>",
                    )
                    ui.html(
                        f"<p style='font-size: 12px; color: var(--color-text-secondary);'>Erstellt: {format_relative_time(conversation.get('created_at'))}</p>",
                    )
                    ui.html(
                        f"<p style='font-size: 12px; color: var(--color-text-secondary);'>Nachrichten: {conversation.get('message_count', 0)}</p>",
                    )

                # Actions
                with ui.element("div").classes("flex space-x-2"):
                    # Open conversation
                    ui.button(
                        icon="open_in_new",
                        on_click=lambda c=conversation: self.open_conversation(c),
                    ).classes("w-8 h-8 bg-blue-500 text-white rounded")

                    # Archive/Unarchive
                    if conversation.get("is_active"):
                        ui.button(
                            icon="archive",
                            on_click=lambda c=conversation: self.archive_conversation(
                                c,
                            ),
                        ).classes("w-8 h-8 bg-gray-500 text-white rounded")
                    else:
                        ui.button(
                            icon="unarchive",
                            on_click=lambda c=conversation: self.unarchive_conversation(
                                c,
                            ),
                        ).classes("w-8 h-8 bg-green-500 text-white rounded")

                    # Delete
                    ui.button(
                        icon="delete",
                        on_click=lambda c=conversation: self.delete_conversation(c),
                    ).classes("w-8 h-8 bg-red-500 text-white rounded")

    def handle_search_change(self, e):
        """Handle search input change."""
        self.search_query = e.value
        self.display_conversations()

    def handle_assistant_filter_change(self, e):
        """Handle assistant filter change."""
        self.selected_assistant_filter = e.value
        self.display_conversations()

    def handle_status_filter_change(self, e):
        """Handle status filter change."""
        self.selected_status_filter = e.value
        self.display_conversations()

    def clear_filters(self):
        """Clear all filters."""
        self.search_query = ""
        self.selected_assistant_filter = "alle"
        self.selected_status_filter = "alle"

        if self.search_input:
            self.search_input.value = ""

        self.display_conversations()

    def show_create_conversation_dialog(self):
        """Show create conversation dialog."""
        with ui.dialog() as dialog, ui.card():
            ui.html(
                "<h2 style='font-size: 20px; font-weight: 600; color: var(--color-text); margin-bottom: 16px;'>Neue Konversation</h2>",
            )

            # Assistant selection
            assistant_options = [
                assistant.get("name", "") for assistant in self.assistants
            ]
            selected_assistant = ui.select(
                "Assistent auswählen",
                options=assistant_options,
                value=assistant_options[0] if assistant_options else None,
            ).classes("w-full mb-4")

            # Title input
            title_input = ui.input(
                placeholder="Konversationstitel (optional)",
                label="Titel",
            ).classes("w-full mb-4")

            # Buttons
            with ui.element("div").classes("flex justify-end space-x-2"):
                ui.button("Abbrechen", on_click=dialog.close).classes(
                    "bg-gray-500 text-white",
                )
                ui.button(
                    "Erstellen",
                    on_click=lambda: self.create_conversation(
                        selected_assistant.value, title_input.value, dialog,
                    ),
                ).classes("bg-blue-600 text-white")

    async def create_conversation(self, assistant_name: str, title: str, dialog):
        """Create a new conversation."""
        try:
            # Find assistant by name
            assistant = next(
                (a for a in self.assistants if a.get("name") == assistant_name), None,
            )
            if not assistant:
                ui.notify("Assistent nicht gefunden", type="negative")
                return

            # Create conversation
            conversation = await conversation_service.create_conversation(
                assistant_id=assistant.get("id"),
                title=title or f"Neue Konversation mit {assistant_name}",
            )

            if conversation:
                # Add to list and refresh
                self.conversations.insert(0, conversation)
                self.display_conversations()

                ui.notify("Konversation erstellt", type="positive")
                dialog.close()

                # Open the new conversation
                await self.open_conversation(conversation)
            else:
                ui.notify("Fehler beim Erstellen der Konversation", type="negative")

        except Exception as e:
            handle_network_error(e, "Erstellen der Konversation")
            ui.notify(
                f"Fehler beim Erstellen der Konversation: {str(e)}", type="negative",
            )

    async def open_conversation(self, conversation: dict[str, Any]):
        """Open a conversation in the chat page."""
        try:
            # Navigate to chat page with conversation ID
            from utils.router import router

            router.navigate_to(f"chat?conversation_id={conversation.get('id')}")
        except Exception as e:
            ui.notify(f"Fehler beim Öffnen der Konversation: {str(e)}", type="negative")

    async def archive_conversation(self, conversation: dict[str, Any]):
        """Archive a conversation."""
        try:
            success = await conversation_service.archive_conversation(
                conversation.get("id"),
            )
            if success:
                conversation["is_active"] = False
                self.display_conversations()
                ui.notify("Konversation archiviert", type="positive")
            else:
                ui.notify("Fehler beim Archivieren der Konversation", type="negative")
        except Exception as e:
            handle_network_error(e, "Archivieren der Konversation")

    async def unarchive_conversation(self, conversation: dict[str, Any]):
        """Unarchive a conversation."""
        try:
            success = await conversation_service.unarchive_conversation(
                conversation.get("id"),
            )
            if success:
                conversation["is_active"] = True
                self.display_conversations()
                ui.notify("Konversation wiederhergestellt", type="positive")
            else:
                ui.notify(
                    "Fehler beim Wiederherstellen der Konversation", type="negative",
                )
        except Exception as e:
            handle_network_error(e, "Wiederherstellen der Konversation")

    async def delete_conversation(self, conversation: dict[str, Any]):
        """Delete a conversation."""
        # Show confirmation dialog
        with ui.dialog() as dialog, ui.card():
            ui.html(
                "<h3 style='font-size: 18px; font-weight: 600; color: var(--color-text); margin-bottom: 16px;'>Konversation löschen</h3>",
            )
            ui.html(
                f"<p style='color: var(--color-text-secondary); margin-bottom: 16px;'>Möchtest du die Konversation '{conversation.get('title')}' wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.</p>",
            )

            with ui.element("div").classes("flex justify-end space-x-2"):
                ui.button("Abbrechen", on_click=dialog.close).classes(
                    "bg-gray-500 text-white",
                )
                ui.button(
                    "Löschen",
                    on_click=lambda: self.confirm_delete_conversation(
                        conversation, dialog,
                    ),
                ).classes("bg-red-600 text-white")

    async def confirm_delete_conversation(self, conversation: dict[str, Any], dialog):
        """Confirm and delete conversation."""
        try:
            success = await conversation_service.delete_conversation(
                conversation.get("id"),
            )
            if success:
                self.conversations = [
                    c
                    for c in self.conversations
                    if c.get("id") != conversation.get("id")
                ]
                self.display_conversations()
                ui.notify("Konversation gelöscht", type="positive")
                dialog.close()
            else:
                ui.notify("Fehler beim Löschen der Konversation", type="negative")
        except Exception as e:
            handle_network_error(e, "Löschen der Konversation")

    async def connect_websocket(self):
        """Connect to WebSocket for real-time updates."""
        try:
            # Connect to general WebSocket for conversation updates
            await websocket_service.connect("general")
            self.websocket_connected = True

            # Set up message handlers
            websocket_service.on_message("conversation_updated")(
                self.handle_conversation_update,
            )
            websocket_service.on_message("conversation_created")(
                self.handle_conversation_created,
            )
            websocket_service.on_message("conversation_deleted")(
                self.handle_conversation_deleted,
            )

        except Exception as e:
            handle_network_error(e, "WebSocket-Verbindung")

    def handle_conversation_update(self, data: dict[str, Any]):
        """Handle conversation update from WebSocket."""
        conversation_id = data.get("conversation_id")
        if conversation_id:
            # Update conversation in list
            for i, conv in enumerate(self.conversations):
                if conv.get("id") == conversation_id:
                    self.conversations[i].update(data)
                    break
            self.display_conversations()

    def handle_conversation_created(self, data: dict[str, Any]):
        """Handle new conversation from WebSocket."""
        self.conversations.insert(0, data)
        self.display_conversations()
        ui.notify("Neue Konversation empfangen", type="info")

    def handle_conversation_deleted(self, data: dict[str, Any]):
        """Handle conversation deletion from WebSocket."""
        conversation_id = data.get("conversation_id")
        if conversation_id:
            self.conversations = [
                c for c in self.conversations if c.get("id") != conversation_id
            ]
            self.display_conversations()
            ui.notify("Konversation gelöscht", type="info")


def create_page():
    """Create and return a conversations page instance."""
    return ConversationsPage()
