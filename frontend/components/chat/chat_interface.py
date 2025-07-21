"""
Chat interface component for real-time messaging.

This module provides a comprehensive chat interface with message
history, input area, and real-time messaging capabilities.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from nicegui import ui

from services.api_client import api_client
from services.websocket_service import websocket_service


class ChatMessage:
    """Chat message data model."""
    
    def __init__(self, content: str, sender: str, timestamp: datetime, message_type: str = "text", message_id: Optional[str] = None):
        """
        Initialize a chat message.
        
        Args:
            content: Message content
            sender: Message sender (user or assistant)
            timestamp: Message timestamp
            message_type: Type of message (text, image, file, etc.)
            message_id: Unique message ID
        """
        self.content = content
        self.sender = sender
        self.timestamp = timestamp
        self.message_type = message_type
        self.id = message_id or f"{sender}_{timestamp.timestamp()}"


class ChatInterface:
    """Chat interface component."""
    
    def __init__(self, conversation_id: Optional[str] = None):
        """
        Initialize the chat interface.
        
        Args:
            conversation_id: ID of the conversation
        """
        self.conversation_id = conversation_id
        self.messages: List[ChatMessage] = []
        self.current_input = ""
        self.is_loading = False
        self.selected_assistant = "general"
        self.websocket_connected = False
        self.typing_users: set = set()
        
        # Initialize WebSocket handlers
        self._setup_websocket_handlers()
        
        # Load initial messages
        asyncio.create_task(self.load_messages())
        
        # Connect to WebSocket if conversation_id is provided
        if self.conversation_id:
            asyncio.create_task(self._connect_websocket())
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket message handlers."""
        @websocket_service.on_message("message")
        async def handle_chat_message(data: Dict[str, Any]):
            """Handle incoming chat message."""
            message_data = data.get("message", {})
            message = ChatMessage(
                content=message_data.get("content", ""),
                sender=message_data.get("user_id", "unknown"),
                timestamp=datetime.fromisoformat(message_data.get("timestamp", datetime.now().isoformat())),
                message_id=message_data.get("id")
            )
            
            # Add message to UI
            self.messages.append(message)
            self._add_message_to_ui(message)
            
            # Scroll to bottom
            await self._scroll_to_bottom()
        
        @websocket_service.on_message("typing")
        async def handle_typing_indicator(data: Dict[str, Any]):
            """Handle typing indicator."""
            user_id = data.get("user_id")
            is_typing = data.get("typing", False)
            
            if is_typing:
                self.typing_users.add(user_id)
            else:
                self.typing_users.discard(user_id)
            
            self._update_typing_indicator()
        
        @websocket_service.on_message("connection_established")
        async def handle_connection_established(data: Dict[str, Any]):
            """Handle WebSocket connection established."""
            self.websocket_connected = True
            ui.notify("Verbunden mit Chat-Server", type="positive")
            # Join conversation after connection
            await websocket_service.join_conversation()
        
        websocket_service.on_connect(self._on_websocket_connect)
        websocket_service.on_disconnect(self._on_websocket_disconnect)
    
    async def _connect_websocket(self):
        """Connect to WebSocket for real-time chat."""
        try:
            await websocket_service.connect(self.conversation_id)
        except Exception as e:
            ui.notify(f"WebSocket-Verbindung fehlgeschlagen: {str(e)}", type="negative")
    
    async def _on_websocket_connect(self):
        """Handle WebSocket connection."""
        self.websocket_connected = True
        ui.notify("Echtzeit-Chat verbunden", type="positive")
        self._create_chat_header()  # Update status dot
    
    async def _on_websocket_disconnect(self):
        """Handle WebSocket disconnection."""
        self.websocket_connected = False
        ui.notify("Echtzeit-Chat getrennt", type="warning")
        self._create_chat_header()  # Update status dot
    
    def _update_typing_indicator(self):
        """Update typing indicator in UI."""
        # Show typing indicator below messages area
        if hasattr(self, 'typing_indicator_element'):
            self.typing_indicator_element.clear()
        if self.typing_users:
            users_text = ", ".join(self.typing_users)
            with ui.element("div") as typing_el:
                typing_el.classes("flex items-center space-x-2 mt-2 mb-2")
                ui.spinner("dots").classes("h-4 w-4")
                ui.html(f"<span style='font-size: 13px; color: var(--color-text-secondary);'>{users_text} schreibt...</span>")
            self.typing_indicator_element = typing_el
        else:
            self.typing_indicator_element = ui.element("div")  # empty
    
    async def _scroll_to_bottom(self):
        """Scroll messages area to bottom."""
        try:
            if self.messages_container:
                # Use JavaScript to scroll to bottom
                await ui.run_javascript("""
                    const messagesContainer = document.querySelector('.messages-container');
                    if (messagesContainer) {
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    }
                """)
        except Exception as e:
            print(f"Error scrolling to bottom: {e}")
    
    def create_chat_interface(self) -> ui.element:
        """
        Create the chat interface.
        
        Returns:
            ui.element: The chat interface container
        """
        with ui.element("div").classes("h-full flex flex-col bg-white dark:bg-gray-800") as chat_interface:
            # Header
            self._create_chat_header()
            
            # Messages area
            self._create_messages_area()
            
            # Input area
            self._create_input_area()
        
        return chat_interface
    
    def _create_chat_header(self):
        """Create the chat header."""
        with ui.element("div").classes("flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"):
            with ui.element("div").classes("flex items-center space-x-3"):
                ui.icon("chat").classes("h-6 w-6 text-blue-600 dark:text-blue-400")
                # Connection status indicator
                status_color = "#22c55e" if self.websocket_connected else "#ef4444"
                status_title = "Verbunden" if self.websocket_connected else "Getrennt"
                ui.html(f'<span title="{status_title}" style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{status_color};margin-left:4px;"></span>')
                with ui.element("div"):
                    ui.html("<h2 style='font-size: 18px; font-weight: 600; color: var(--color-text);'>Chat</h2>")
                    ui.html("<p style='font-size: 14px; color: var(--color-text-secondary);'>Konversation mit AI-Assistenten</p>")
            
            with ui.element("div").classes("flex items-center space-x-2"):
                # Assistant selector
                with ui.select(
                    options=[
                        {"label": "Allgemeiner Assistent", "value": "general"},
                        {"label": "Code Assistant", "value": "code"},
                        {"label": "Data Analyst", "value": "data"},
                        {"label": "Creative Writer", "value": "creative"}
                    ],
                    value=self.selected_assistant,
                    on_change=self._handle_assistant_change
                ).classes("w-48"):
                    ui.option("general", "Allgemeiner Assistent")
                    ui.option("code", "Code Assistant")
                    ui.option("data", "Data Analyst")
                    ui.option("creative", "Creative Writer")
                
                # Settings button
                ui.button(
                    icon="settings",
                    on_click=self._handle_settings
                ).classes("p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700")
    
    def _create_messages_area(self):
        """Create the messages area."""
        with ui.element("div").classes("flex-1 overflow-y-auto p-4 space-y-4") as messages_area:
            self.messages_container = messages_area
    
    def _create_input_area(self):
        """Create the input area."""
        with ui.element("div").classes("p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"):
            with ui.element("div").classes("flex space-x-2"):
                # Message input
                self.message_input = ui.textarea(
                    placeholder="Nachricht eingeben...",
                    on_change=self._handle_input_change
                ).classes("flex-1 resize-none")
                
                # Send button
                ui.button(
                    "Senden",
                    icon="send",
                    on_click=self._handle_send_message
                ).classes("bg-blue-600 text-white")
    
    async def load_messages(self):
        """Load existing messages."""
        if not self.conversation_id:
            return
        
        try:
            # Load messages from API
            messages = await api_client.get_conversation_messages(self.conversation_id)
            
            for msg_data in messages:
                message = ChatMessage(
                    content=msg_data.get("content", ""),
                    sender=msg_data.get("user_id", "unknown"),
                    timestamp=datetime.fromisoformat(msg_data.get("timestamp", datetime.now().isoformat())),
                    message_id=msg_data.get("id")
                )
                self.messages.append(message)
                self._add_message_to_ui(message)
        
        except Exception as e:
            ui.notify(f"Fehler beim Laden der Nachrichten: {str(e)}", type="negative")
    
    def _add_message_to_ui(self, message: ChatMessage):
        """Add a message to the UI."""
        is_user = message.sender == "user"
        with self.messages_container:
            with ui.element("div").classes(f"flex {'justify-end' if is_user else 'justify-start'}"):
                with ui.element("div").classes(f"max-w-xs lg:max-w-md {'bg-blue-600 text-white' if is_user else 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'} rounded-lg px-4 py-2 shadow-sm"):
                    # Message content
                    ui.html(f"<p style='font-size: 14px; line-height: 1.4;'>{message.content}</p>")
                    
                    # Message timestamp
                    time_str = message.timestamp.strftime("%H:%M")
                    ui.html(f"<p style='font-size: 11px; opacity: 0.7; margin-top: 4px; text-align: {'right' if is_user else 'left'};'>{time_str}</p>")
        # Show feedback for new message
        if is_user:
            ui.notify("Nachricht gesendet", type="positive")
        else:
            ui.notify("Neue Nachricht empfangen", type="info")
    
    def _handle_input_change(self, e):
        """Handle input change."""
        self.current_input = e.value
        
        # Auto-resize textarea
        if hasattr(self, 'message_input'):
            try:
                # Auto-resize textarea based on content
                lines = len(e.value.split('\n'))
                min_height = 40
                max_height = 120
                new_height = min(max(lines * 20, min_height), max_height)
                
                # Update textarea height using JavaScript
                ui.run_javascript(f"""
                    const textarea = document.querySelector('textarea[placeholder="Nachricht eingeben..."]');
                    if (textarea) {{
                        textarea.style.height = '{new_height}px';
                    }}
                """)
            except Exception as e:
                print(f"Error auto-resizing textarea: {e}")
    
    def _handle_send_message(self):
        """Handle send message."""
        if not self.current_input.strip():
            return
        
        # Add user message
        user_message = ChatMessage(
            content=self.current_input,
            sender="user",
            timestamp=datetime.now()
        )
        self.messages.append(user_message)
        self._add_message_to_ui(user_message)
        
        # Clear input
        self.current_input = ""
        if hasattr(self, 'message_input'):
            self.message_input.value = ""
        
        # Send to WebSocket if connected, otherwise to API
        if self.websocket_connected:
            asyncio.create_task(self._send_message_to_websocket(user_message.content))
        else:
            asyncio.create_task(self._send_message_to_api(user_message.content))
    
    async def _send_message_to_websocket(self, content: str):
        """Send message via WebSocket."""
        try:
            await websocket_service.send_chat_message(content)
        except Exception as e:
            ui.notify(f"Fehler beim Senden der Nachricht: {str(e)}", type="negative")
    
    async def _send_message_to_api(self, content: str):
        """Send message to API and get response."""
        self.is_loading = True
        
        try:
            # Show typing indicator
            self._show_typing_indicator()
            
            # Send message to API
            response = await api_client.send_message(self.conversation_id, content)
            
            if response:
                # Create assistant response
                assistant_message = ChatMessage(
                    content=response.get("content", "Keine Antwort erhalten"),
                    sender="assistant",
                    timestamp=datetime.now()
                )
                
                self.messages.append(assistant_message)
                self._add_message_to_ui(assistant_message)
            
        except Exception as e:
            ui.notify(f"Fehler beim Senden der Nachricht: {str(e)}", type="negative")
        
        finally:
            self.is_loading = False
            self._hide_typing_indicator()
    
    def _show_typing_indicator(self):
        """Show typing indicator."""
        try:
            if hasattr(self, 'typing_indicator_element'):
                self.typing_indicator_element.visible = True
                # Animate typing indicator
                ui.run_javascript("""
                    const typingIndicator = document.querySelector('.typing-indicator');
                    if (typingIndicator) {
                        typingIndicator.style.display = 'flex';
                        typingIndicator.style.animation = 'typing 1.4s infinite';
                    }
                """)
        except Exception as e:
            print(f"Error showing typing indicator: {e}")
    
    def _hide_typing_indicator(self):
        """Hide typing indicator."""
        try:
            if hasattr(self, 'typing_indicator_element'):
                self.typing_indicator_element.visible = False
                # Stop animation
                ui.run_javascript("""
                    const typingIndicator = document.querySelector('.typing-indicator');
                    if (typingIndicator) {
                        typingIndicator.style.display = 'none';
                        typingIndicator.style.animation = 'none';
                    }
                """)
        except Exception as e:
            print(f"Error hiding typing indicator: {e}")
    
    def _handle_assistant_change(self, e):
        """Handle assistant change."""
        self.selected_assistant = e.value
        ui.notify(f"Assistent gewechselt zu: {e.value}", type="info")
    
    def _handle_settings(self):
        """Handle settings button."""
        ui.notify("Chat-Einstellungen werden geöffnet...", type="info")


def create_chat_interface(conversation_id: Optional[str] = None) -> ui.element:
    """
    Create and return a chat interface.
    
    Args:
        conversation_id: ID of the conversation (optional)
        
    Returns:
        ui.element: The chat interface
    """
    chat = ChatInterface(conversation_id)
    return chat.create_chat_interface() 