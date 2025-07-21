"""
Chat page for the AI Assistant Platform.

This module provides the main chat interface with real-time messaging,
conversation management, and assistant integration.
"""

import asyncio
from datetime import datetime

from components.common.error_message import ErrorSeverity, create_error_message
from components.common.loading_spinner import create_loading_spinner
from nicegui import app, ui
from services.assistant_service import assistant_service
from services.conversation_service import conversation_service
from services.error_handler import handle_network_error
from services.websocket_service import websocket_service
from utils.helpers import format_relative_time


class ChatPage:
    """Chat page with real-time messaging."""

    def __init__(self):
        """Initialize chat page."""
        self.current_conversation_id = None
        self.current_assistant = None
        self.messages = []
        self.is_loading = False
        self.is_sending = False

        # UI Components
        self.messages_container = None
        self.input_container = None
        self.conversation_header = None
        self.loading_spinner = None
        self.error_component = None
        self.message_input = None
        self.send_button = None

        # WebSocket connection
        self.websocket_connected = False

        self.create_chat_interface()
        self.initialize_chat()

    def create_chat_interface(self):
        """Create the chat interface UI."""
        with ui.column().classes("h-screen flex flex-col"):
            # Header
            self.create_conversation_header()

            # Messages Area
            with ui.element("div").classes("flex-1 overflow-hidden"):
                self.messages_container = ui.element("div").classes(
                    "h-full overflow-y-auto p-4 space-y-4",
                )

            # Input Area
            self.create_input_area()

            # Loading and Error States
            self.loading_spinner = create_loading_spinner(
                "Lade Konversation...", size="lg",
            )
            self.error_component = create_error_message("", dismissible=True)

    def create_conversation_header(self):
        """Create conversation header."""
        self.conversation_header = ui.element("div").classes(
            "bg-white border-b border-gray-200 p-4",
        )

        with self.conversation_header:
            with ui.row().classes("items-center justify-between"):
                with ui.element("div"):
                    ui.label("Chat").classes("text-lg font-semibold text-gray-900")
                    ui.label("Wähle eine Konversation aus").classes(
                        "text-sm text-gray-600",
                    )

                with ui.row().classes("space-x-2"):
                    ui.button(
                        "Neue Konversation",
                        icon="add",
                        on_click=self.create_new_conversation,
                    ).classes("bg-blue-600 text-white")

                    ui.button(
                        "Konversationen",
                        icon="list",
                        on_click=self.show_conversations,
                    ).classes("bg-gray-600 text-white")

    def create_input_area(self):
        """Create message input area."""
        self.input_container = ui.element("div").classes(
            "bg-white border-t border-gray-200 p-4",
        )

        with self.input_container:
            with ui.row().classes("items-end space-x-2"):
                # Message input
                self.message_input = ui.textarea(
                    placeholder="Nachricht eingeben...",
                    rows=1,
                    on_keydown=self.handle_keydown,
                ).classes("flex-1 resize-none")

                # Send button
                self.send_button = ui.button(
                    "Senden",
                    icon="send",
                    on_click=self.send_message,
                ).classes("bg-blue-600 text-white px-4 py-2")

    async def initialize_chat(self):
        """Initialize chat with conversation data."""
        try:
            # Get conversation ID from storage or URL
            self.current_conversation_id = app.storage.user.get(
                "current_conversation_id",
            )

            if not self.current_conversation_id:
                # Try to get from URL parameters
                # This would need to be implemented based on your routing
                await self.create_new_conversation()
                return

            # Load conversation and messages
            await self.load_conversation()

        except Exception as e:
            handle_network_error(e, "Initialisierung des Chats")
            self.error_component.update_message(
                f"Fehler bei der Chat-Initialisierung: {str(e)}",
                ErrorSeverity.ERROR,
            )
            self.error_component.show()

    async def load_conversation(self):
        """Load conversation and messages."""
        if not self.current_conversation_id:
            return

        self.is_loading = True
        self.loading_spinner.show()
        self.error_component.hide()

        try:
            # Load conversation details
            conversation = conversation_service.get_conversation_by_id(
                self.current_conversation_id,
            )
            if not conversation:
                conversation = await conversation_service.get_conversation(
                    self.current_conversation_id,
                )

            if conversation:
                self.current_assistant = await assistant_service.get_assistant(
                    conversation.assistant_id,
                )
                self.update_conversation_header(conversation)

                # Load messages
                self.messages = await conversation_service.get_conversation_messages(
                    self.current_conversation_id,
                )
                self.display_messages()

                # Connect to WebSocket for real-time updates
                await self.connect_websocket()
            else:
                self.error_component.update_message(
                    "Konversation nicht gefunden",
                    ErrorSeverity.ERROR,
                )
                self.error_component.show()

        except Exception as e:
            handle_network_error(e, "Laden der Konversation")
            self.error_component.update_message(
                f"Fehler beim Laden der Konversation: {str(e)}",
                ErrorSeverity.ERROR,
            )
            self.error_component.show()

        finally:
            self.is_loading = False
            self.loading_spinner.hide()

    def update_conversation_header(self, conversation):
        """Update conversation header with conversation details."""
        self.conversation_header.clear()

        with self.conversation_header:
            with ui.row().classes("items-center justify-between"):
                with ui.element("div"):
                    ui.label(conversation.title).classes(
                        "text-lg font-semibold text-gray-900",
                    )
                    assistant_name = (
                        self.current_assistant.name
                        if self.current_assistant
                        else "Unbekannter Assistent"
                    )
                    ui.label(f"mit {assistant_name}").classes("text-sm text-gray-600")

                with ui.row().classes("space-x-2"):
                    ui.button(
                        "Archivieren",
                        icon="archive",
                        on_click=lambda: self.archive_conversation(),
                    ).classes("bg-gray-600 text-white")

                    ui.button(
                        "Löschen",
                        icon="delete",
                        on_click=lambda: self.delete_conversation(),
                    ).classes("bg-red-600 text-white")

    def display_messages(self):
        """Display messages in the chat interface."""
        self.messages_container.clear()

        if not self.messages:
            with self.messages_container:
                with ui.element("div").classes("text-center py-8"):
                    ui.icon("chat_bubble_outline").classes(
                        "w-12 h-12 text-gray-400 mx-auto mb-2",
                    )
                    ui.label("Keine Nachrichten vorhanden").classes("text-gray-500")
                    ui.label("Starte eine Konversation mit deinem Assistenten").classes(
                        "text-sm text-gray-400",
                    )
            return

        with self.messages_container:
            for message in self.messages:
                self.create_message_bubble(message)

        # Scroll to bottom
        self.scroll_to_bottom()

    def create_message_bubble(self, message):
        """Create a message bubble."""
        is_user = message.role == "user"

        with ui.element("div").classes(
            "flex",
            "justify-end" if is_user else "justify-start",
        ):
            with ui.element("div").classes(
                "max-w-xs lg:max-w-md px-4 py-2 rounded-lg",
                "bg-blue-600 text-white" if is_user else "bg-gray-200 text-gray-900",
            ):
                # Message content
                ui.label(message.content).classes("text-sm")

                # Message metadata
                with ui.row().classes("items-center justify-between mt-1"):
                    ui.label(format_relative_time(message.timestamp)).classes(
                        "text-xs",
                        "text-blue-200" if is_user else "text-gray-500",
                    )

                    if message.tool_results:
                        ui.icon("build").classes(
                            "w-4 h-4",
                            "text-blue-200" if is_user else "text-gray-500",
                        )

    async def send_message(self):
        """Send a message."""
        if not self.message_input.value or self.is_sending:
            return

        message_content = self.message_input.value.strip()
        self.message_input.value = ""
        self.is_sending = True
        self.send_button.disable()

        try:
            # Add user message to UI immediately
            user_message = {
                "id": f"temp_{datetime.now().timestamp()}",
                "content": message_content,
                "role": "user",
                "timestamp": datetime.now(),
                "is_loading": False,
            }
            self.messages.append(user_message)
            self.display_messages()

            # Send message to API
            if self.current_conversation_id:
                sent_message = await conversation_service.send_message(
                    self.current_conversation_id,
                    message_content,
                )

                if sent_message:
                    # Update message in list
                    for i, msg in enumerate(self.messages):
                        if msg["id"] == user_message["id"]:
                            self.messages[i] = sent_message
                            break

                    self.display_messages()
                else:
                    # Remove failed message
                    self.messages = [
                        msg for msg in self.messages if msg["id"] != user_message["id"]
                    ]
                    self.display_messages()

                    self.error_component.update_message(
                        "Fehler beim Senden der Nachricht",
                        ErrorSeverity.ERROR,
                    )
                    self.error_component.show()

        except Exception as e:
            handle_network_error(e, "Senden der Nachricht")
            self.error_component.update_message(
                f"Fehler beim Senden der Nachricht: {str(e)}",
                ErrorSeverity.ERROR,
            )
            self.error_component.show()

        finally:
            self.is_sending = False
            self.send_button.enable()

    def handle_keydown(self, event):
        """Handle keydown events in message input."""
        if event.key == "Enter" and not event.shift_key:
            event.preventDefault()
            asyncio.create_task(self.send_message())

    async def connect_websocket(self):
        """Connect to WebSocket for real-time updates."""
        try:
            if self.current_conversation_id:
                await websocket_service.connect(self.current_conversation_id)
                self.websocket_connected = True

                # Set up message handler
                websocket_service.on_message(self.handle_websocket_message)
        except Exception as e:
            handle_network_error(e, "WebSocket-Verbindung")

    def handle_websocket_message(self, message_data):
        """Handle incoming WebSocket messages."""
        try:
            # Add assistant message to UI
            assistant_message = {
                "id": message_data.get("id"),
                "content": message_data.get("content", ""),
                "role": "assistant",
                "timestamp": datetime.now(),
                "tool_results": message_data.get("tool_results"),
                "is_loading": False,
            }

            self.messages.append(assistant_message)
            self.display_messages()

        except Exception as e:
            handle_network_error(e, "Verarbeitung der WebSocket-Nachricht")

    async def create_new_conversation(self):
        """Create a new conversation."""
        try:
            # Get first available assistant
            assistants = assistant_service.get_active_assistants()
            if not assistants:
                self.error_component.update_message(
                    "Keine aktiven Assistenten verfügbar",
                    ErrorSeverity.WARNING,
                )
                self.error_component.show()
                return

            assistant = assistants[0]
            conversation = await conversation_service.create_conversation(assistant.id)

            if conversation:
                self.current_conversation_id = conversation.id
                app.storage.user["current_conversation_id"] = conversation.id
                await self.load_conversation()
            else:
                self.error_component.update_message(
                    "Fehler beim Erstellen der Konversation",
                    ErrorSeverity.ERROR,
                )
                self.error_component.show()

        except Exception as e:
            handle_network_error(e, "Erstellen der Konversation")
            self.error_component.update_message(
                f"Fehler beim Erstellen der Konversation: {str(e)}",
                ErrorSeverity.ERROR,
            )
            self.error_component.show()

    def show_conversations(self):
        """Navigate to conversations page."""
        ui.navigate.to("/conversations")

    async def archive_conversation(self):
        """Archive current conversation."""
        if not self.current_conversation_id:
            return

        try:
            success = await conversation_service.archive_conversation(
                self.current_conversation_id,
            )
            if success:
                ui.navigate.to("/conversations")
            else:
                self.error_component.update_message(
                    "Fehler beim Archivieren der Konversation",
                    ErrorSeverity.ERROR,
                )
                self.error_component.show()

        except Exception as e:
            handle_network_error(e, "Archivieren der Konversation")
            self.error_component.update_message(
                f"Fehler beim Archivieren der Konversation: {str(e)}",
                ErrorSeverity.ERROR,
            )
            self.error_component.show()

    async def delete_conversation(self):
        """Delete current conversation."""
        if not self.current_conversation_id:
            return

        try:
            success = await conversation_service.delete_conversation(
                self.current_conversation_id,
            )
            if success:
                ui.navigate.to("/conversations")
            else:
                self.error_component.update_message(
                    "Fehler beim Löschen der Konversation",
                    ErrorSeverity.ERROR,
                )
                self.error_component.show()

        except Exception as e:
            handle_network_error(e, "Löschen der Konversation")
            self.error_component.update_message(
                f"Fehler beim Löschen der Konversation: {str(e)}",
                ErrorSeverity.ERROR,
            )
            self.error_component.show()

    def scroll_to_bottom(self):
        """Scroll messages container to bottom."""
        # This would need to be implemented based on your UI framework


def create_page():
    """Create and return a chat page instance."""
    return ChatPage()


# Register the page
@ui.page("/chat")
def chat_page():
    """Chat page route."""
    return create_page()
