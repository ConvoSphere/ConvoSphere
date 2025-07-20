"""
Advanced chat input component for the AI Assistant Platform.

This module provides a comprehensive chat input component with support for
text messages, file uploads, tool selection, and message editing.
"""

from nicegui import ui
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import asyncio

from services.message_service import message_service, AdvancedMessage, MessageType
from services.tool_service import tool_service, Tool
from services.file_service import file_service, FileStatus
from utils.helpers import generate_id
from utils.validators import validate_message_data, sanitize_input
from utils.constants import SUPPORTED_FILE_TYPES, MAX_FILE_SIZE


class ChatInput:
    """Advanced chat input component."""
    
    def __init__(
        self,
        conversation_id: str,
        on_message_sent: Optional[Callable[[AdvancedMessage], None]] = None,
        on_file_upload: Optional[Callable[[AdvancedMessage], None]] = None,
        on_tool_executed: Optional[Callable[[AdvancedMessage], None]] = None,
        placeholder: str = "Nachricht eingeben..."
    ):
        """
        Initialize chat input component.
        
        Args:
            conversation_id: Conversation ID
            on_message_sent: Callback for sent messages
            on_file_upload: Callback for file uploads
            on_tool_executed: Callback for tool executions
            placeholder: Input placeholder text
        """
        self.conversation_id = conversation_id
        self.on_message_sent = on_message_sent
        self.on_file_upload = on_file_upload
        self.on_tool_executed = on_tool_executed
        self.placeholder = placeholder
        
        # UI components
        self.container = None
        self.input_field = None
        self.send_button = None
        self.file_button = None
        self.tool_button = None
        self.emoji_button = None
        
        # State
        self.is_sending = False
        self.selected_files: List[Dict[str, Any]] = []
        self.selected_tool: Optional[Tool] = None
        self.reply_to_message: Optional[str] = None
        
        self.create_chat_input()
    
    def create_chat_input(self):
        """Create the chat input UI."""
        self.container = ui.element("div").classes("border-t bg-white p-4")
        
        with self.container:
            # Reply indicator
            self.reply_indicator = ui.element("div").classes("hidden mb-2 p-2 bg-blue-50 rounded")
            
            # File preview
            self.file_preview = ui.element("div").classes("hidden mb-2")
            
            # Tool selection
            self.tool_selection = ui.element("div").classes("hidden mb-2 p-2 bg-gray-50 rounded")
            
            # Main input area
            with ui.row().classes("items-end space-x-2"):
                # Input field
                self.input_field = ui.textarea(
                    placeholder=self.placeholder,
                    rows=1,
                    on_keydown=self.handle_keydown
                ).classes("flex-1 resize-none").props("autogrow")
                
                # Action buttons
                with ui.column().classes("space-y-1"):
                    # Emoji button
                    self.emoji_button = ui.button(
                        icon="emoji_emotions",
                        on_click=self.show_emoji_picker
                    ).classes("w-8 h-8 bg-gray-100 text-gray-600")
                    
                    # File upload button
                    self.file_button = ui.button(
                        icon="attach_file",
                        on_click=self.show_file_picker
                    ).classes("w-8 h-8 bg-gray-100 text-gray-600")
                    
                    # Tool selection button
                    self.tool_button = ui.button(
                        icon="build",
                        on_click=self.show_tool_picker
                    ).classes("w-8 h-8 bg-gray-100 text-gray-600")
                    
                    # Send button
                    self.send_button = ui.button(
                        icon="send",
                        on_click=self.send_message
                    ).classes("w-8 h-8 bg-blue-600 text-white")
    
    def handle_keydown(self, event):
        """Handle keyboard events."""
        if event.key == "Enter" and not event.shift_key:
            event.preventDefault()
            self.send_message()
    
    async def send_message(self):
        """Send the current message."""
        if self.is_sending:
            return
        
        content = self.input_field.value.strip()
        if not content and not self.selected_files:
            return
        
        self.is_sending = True
        self.send_button.disable()
        
        try:
            # Send files first
            if self.selected_files:
                for file_info in self.selected_files:
                    message = await message_service.send_file_message(
                        self.conversation_id,
                        file_info["data"],
                        file_info["name"],
                        file_info["type"],
                        self.reply_to_message
                    )
                    
                    if message and self.on_file_upload:
                        self.on_file_upload(message)
            
            # Send text message
            if content:
                message = await message_service.send_text_message(
                    self.conversation_id,
                    content,
                    self.reply_to_message
                )
                
                if message and self.on_message_sent:
                    self.on_message_sent(message)
            
            # Execute tool if selected
            if self.selected_tool:
                tool_input = self.parse_tool_input(content)
                if tool_input:
                    message = await message_service.execute_tool(
                        self.conversation_id,
                        self.selected_tool.id,
                        tool_input,
                        self.reply_to_message
                    )
                    
                    if message and self.on_tool_executed:
                        self.on_tool_executed(message)
            
            # Clear input and reset state
            self.clear_input()
            
        except Exception as e:
            ui.notify(f"Fehler beim Senden: {str(e)}", type="error")
        finally:
            self.is_sending = False
            self.send_button.enable()
    
    def parse_tool_input(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse tool input from message content."""
        if not self.selected_tool:
            return None
        
        # Simple parsing - in a real implementation, you might use NLP
        # or structured input parsing
        try:
            # For now, just return a basic structure
            return {"input": content}
        except Exception:
            return None
    
    def show_file_picker(self):
        """Show file picker dialog."""
        ui.upload(
            label="Dateien auswählen",
            multiple=True,
            on_upload=self.handle_file_upload
        ).props("accept=" + ",".join(SUPPORTED_FILE_TYPES))
    
    async def handle_file_upload(self, event):
        """Handle file upload using file service."""
        for file in event.files:
            if file.size > MAX_FILE_SIZE:
                ui.notify(f"Datei {file.name} ist zu groß (max {MAX_FILE_SIZE} bytes)", type="error")
                continue
            
            # Validate file using file service
            validation = file_service.validate_file(file.content, file.name, file.type)
            if not validation["valid"]:
                error_msg = "; ".join(validation["errors"])
                ui.notify(f"Datei {file.name}: {error_msg}", type="error")
                continue
            
            file_info = {
                "name": file.name,
                "type": file.type,
                "size": file.size,
                "data": file.content,
                "file_id": None,
                "upload_progress": 0.0
            }
            
            self.selected_files.append(file_info)
            
            # Start upload with progress tracking
            await self.upload_file_with_progress(file_info)
        
        self.update_file_preview()
    
    async def upload_file_with_progress(self, file_info: Dict[str, Any]):
        """Upload file with progress tracking."""
        try:
            file_id = await file_service.upload_file(
                file_data=file_info["data"],
                filename=file_info["name"],
                mime_type=file_info["type"],
                on_progress=self.update_file_progress,
                on_complete=self.on_file_upload_complete,
                on_error=self.on_file_upload_error
            )
            
            if file_id:
                file_info["file_id"] = file_id
                
        except Exception as e:
            ui.notify(f"Upload fehlgeschlagen für {file_info['name']}: {str(e)}", type="error")
    
    def update_file_progress(self, progress):
        """Update file upload progress."""
        # Find the file in selected_files and update its progress
        for file_info in self.selected_files:
            if file_info["name"] == progress.filename:
                file_info["upload_progress"] = progress.percentage
                break
        
        self.update_file_preview()
    
    def on_file_upload_complete(self, result):
        """Handle file upload completion."""
        file_id = result.get("file_id")
        filename = result.get("filename")
        
        ui.notify(f"Datei {filename} erfolgreich hochgeladen", type="positive")
        
        # Update file info with file ID
        for file_info in self.selected_files:
            if file_info["name"] == filename:
                file_info["file_id"] = file_id
                file_info["upload_progress"] = 100.0
                break
        
        self.update_file_preview()
    
    def on_file_upload_error(self, error_msg):
        """Handle file upload error."""
        ui.notify(f"Upload fehlgeschlagen: {error_msg}", type="error")
    
    def update_file_preview(self):
        """Update file preview display with upload progress."""
        if not self.selected_files:
            self.file_preview.classes("hidden")
            return
        
        self.file_preview.classes("block")
        self.file_preview.clear()
        
        with self.file_preview:
            ui.label("Ausgewählte Dateien:").classes("text-sm font-medium mb-1")
            
            for i, file_info in enumerate(self.selected_files):
                with ui.row().classes("items-center justify-between p-2 border rounded"):
                    # File info
                    with ui.column().classes("flex-1"):
                        ui.label(f"• {file_info['name']}").classes("text-sm font-medium")
                        ui.label(f"{file_info['size']} bytes").classes("text-xs text-gray-500")
                        
                        # Upload progress
                        if file_info["upload_progress"] < 100.0:
                            with ui.row().classes("items-center space-x-2"):
                                ui.linear_progress(
                                    value=file_info["upload_progress"] / 100.0
                                ).classes("flex-1")
                                ui.label(f"{file_info['upload_progress']:.1f}%").classes("text-xs")
                        else:
                            ui.label("✓ Hochgeladen", type="positive").classes("text-xs")
                    
                    # Remove button
                    ui.button(
                        icon="close",
                        on_click=lambda idx=i: self.remove_file(idx)
                    ).classes("w-6 h-6 bg-red-500 text-white text-xs")
    
    def remove_file(self, index: int):
        """Remove file from selection."""
        if 0 <= index < len(self.selected_files):
            self.selected_files.pop(index)
            self.update_file_preview()
    
    def show_tool_picker(self):
        """Show tool picker dialog."""
        # Create tool selection dialog
        with ui.dialog() as dialog, ui.card():
            ui.label("Tool auswählen").classes("text-lg font-medium mb-4")
            
            # Tool categories
            categories = tool_service.get_tool_categories()
            
            for category in categories:
                tools = tool_service.get_tools_by_category(category)
                
                with ui.expansion(category, icon="folder"):
                    for tool in tools:
                        with ui.row().classes("items-center justify-between p-2"):
                            with ui.column():
                                ui.label(tool.name).classes("font-medium")
                                ui.label(tool.description).classes("text-sm text-gray-600")
                            
                            ui.button(
                                "Auswählen",
                                on_click=lambda t=tool: self.select_tool(t, dialog)
                            ).classes("bg-blue-500 text-white px-3 py-1")
    
    def select_tool(self, tool: Tool, dialog):
        """Select a tool."""
        self.selected_tool = tool
        self.update_tool_selection()
        dialog.close()
    
    def update_tool_selection(self):
        """Update tool selection display."""
        if not self.selected_tool:
            self.tool_selection.classes("hidden")
            return
        
        self.tool_selection.classes("block")
        self.tool_selection.clear()
        
        with self.tool_selection:
            with ui.row().classes("items-center justify-between"):
                with ui.column():
                    ui.label(f"Tool: {self.selected_tool.name}").classes("font-medium")
                    ui.label(self.selected_tool.description).classes("text-sm text-gray-600")
                
                ui.button(
                    icon="close",
                    on_click=self.clear_tool_selection
                ).classes("w-6 h-6 bg-red-500 text-white")
    
    def clear_tool_selection(self):
        """Clear tool selection."""
        self.selected_tool = None
        self.tool_selection.classes("hidden")
    
    def show_emoji_picker(self):
        """Show emoji picker."""
        # Simple emoji picker - in a real implementation, you might use a proper emoji library
        emojis = ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇"]
        
        with ui.dialog() as dialog, ui.card():
            ui.label("Emoji auswählen").classes("text-lg font-medium mb-4")
            
            with ui.row().classes("flex-wrap gap-2"):
                for emoji in emojis:
                    ui.button(
                        emoji,
                        on_click=lambda e=emoji: self.insert_emoji(e, dialog)
                    ).classes("text-2xl p-2 hover:bg-gray-100 rounded")
    
    def insert_emoji(self, emoji: str, dialog):
        """Insert emoji into input field."""
        current_value = self.input_field.value or ""
        self.input_field.value = current_value + emoji
        dialog.close()
    
    def set_reply_to(self, message_id: str, message_content: str):
        """Set reply-to message."""
        self.reply_to_message = message_id
        self.update_reply_indicator(message_content)
    
    def update_reply_indicator(self, message_content: str):
        """Update reply indicator display."""
        if not self.reply_to_message:
            self.reply_indicator.classes("hidden")
            return
        
        self.reply_indicator.classes("block")
        self.reply_indicator.clear()
        
        with self.reply_indicator:
            with ui.row().classes("items-center justify-between"):
                with ui.column():
                    ui.label("Antwort auf:").classes("text-xs font-medium")
                    ui.label(message_content[:50] + "..." if len(message_content) > 50 else message_content).classes("text-sm")
                
                ui.button(
                    icon="close",
                    on_click=self.clear_reply_to
                ).classes("w-4 h-4 bg-gray-500 text-white")
    
    def clear_reply_to(self):
        """Clear reply-to message."""
        self.reply_to_message = None
        self.reply_indicator.classes("hidden")
    
    def clear_input(self):
        """Clear input field and reset state."""
        self.input_field.value = ""
        self.selected_files.clear()
        self.selected_tool = None
        self.reply_to_message = None
        
        self.update_file_preview()
        self.update_tool_selection()
        self.update_reply_indicator("")
    
    def focus(self):
        """Focus the input field."""
        if self.input_field:
            self.input_field.focus()
    
    def set_placeholder(self, placeholder: str):
        """Set input placeholder."""
        self.placeholder = placeholder
        if self.input_field:
            self.input_field.props(f"placeholder={placeholder}")
    
    def disable(self):
        """Disable the input component."""
        if self.input_field:
            self.input_field.disable()
        if self.send_button:
            self.send_button.disable()
        if self.file_button:
            self.file_button.disable()
        if self.tool_button:
            self.tool_button.disable()
        if self.emoji_button:
            self.emoji_button.disable()
    
    def enable(self):
        """Enable the input component."""
        if self.input_field:
            self.input_field.enable()
        if self.send_button:
            self.send_button.enable()
        if self.file_button:
            self.file_button.enable()
        if self.tool_button:
            self.tool_button.enable()
        if self.emoji_button:
            self.emoji_button.enable()


def create_chat_input(
    conversation_id: str,
    on_message_sent: Optional[Callable[[AdvancedMessage], None]] = None,
    on_file_upload: Optional[Callable[[AdvancedMessage], None]] = None,
    on_tool_executed: Optional[Callable[[AdvancedMessage], None]] = None,
    placeholder: str = "Nachricht eingeben..."
) -> ChatInput:
    """
    Create a chat input component.
    
    Args:
        conversation_id: Conversation ID
        on_message_sent: Callback for sent messages
        on_file_upload: Callback for file uploads
        on_tool_executed: Callback for tool executions
        placeholder: Input placeholder text
        
    Returns:
        ChatInput instance
    """
    return ChatInput(
        conversation_id=conversation_id,
        on_message_sent=on_message_sent,
        on_file_upload=on_file_upload,
        on_tool_executed=on_tool_executed,
        placeholder=placeholder
    ) 