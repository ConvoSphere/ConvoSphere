"""
Advanced message bubble component for the AI Assistant Platform.

This module provides a comprehensive message bubble component that supports
different message types including text, files, tools, and system messages.
"""

from nicegui import ui
from typing import Optional, Dict, Any, List
from datetime import datetime

from services.message_service import AdvancedMessage, MessageType, MessageStatus
from services.tool_service import ToolExecutionResult
from utils.helpers import format_timestamp, format_relative_time, format_file_size
from utils.constants import SUPPORTED_FILE_TYPES


class MessageBubble:
    """Advanced message bubble component."""
    
    def __init__(self, message: AdvancedMessage):
        """
        Initialize message bubble.
        
        Args:
            message: Message to display
        """
        self.message = message
        self.container = None
        self.content_container = None
        self.metadata_container = None
        
        self.create_message_bubble()
    
    def create_message_bubble(self):
        """Create the message bubble UI."""
        is_user = self.message.role == "user"
        is_system = self.message.role == "system"
        
        # Main container
        self.container = ui.element("div").classes(
            "flex mb-4",
            "justify-end" if is_user else "justify-start"
        )
        
        with self.container:
            # Message bubble
            bubble_classes = [
                "max-w-xs lg:max-w-md px-4 py-3 rounded-lg",
                "bg-blue-600 text-white" if is_user else "bg-gray-200 text-gray-900",
                "bg-red-100 text-red-800 border border-red-300" if is_system else ""
            ]
            
            with ui.element("div").classes(" ".join(bubble_classes)):
                # Content container
                self.content_container = ui.element("div")
                
                # Create content based on message type
                self.create_message_content()
                
                # Metadata container
                self.metadata_container = ui.element("div").classes("mt-2")
                self.create_message_metadata()
    
    def create_message_content(self):
        """Create message content based on type."""
        if self.message.message_type == MessageType.TEXT:
            self.create_text_content()
        elif self.message.message_type == MessageType.FILE:
            self.create_file_content()
        elif self.message.message_type == MessageType.TOOL:
            self.create_tool_content()
        elif self.message.message_type == MessageType.SYSTEM:
            self.create_system_content()
        elif self.message.message_type == MessageType.ERROR:
            self.create_error_content()
        elif self.message.message_type == MessageType.TYPING:
            self.create_typing_content()
        else:
            self.create_text_content()
    
    def create_text_content(self):
        """Create text message content."""
        with self.content_container:
            # Show edited indicator
            if self.message.is_edited:
                ui.label("(bearbeitet)").classes("text-xs opacity-70 mb-1")
            
            # Message content
            ui.label(self.message.content).classes("text-sm whitespace-pre-wrap")
    
    def create_file_content(self):
        """Create file message content."""
        if not self.message.file_attachments:
            return
        
        with self.content_container:
            for file_attachment in self.message.file_attachments:
                with ui.element("div").classes("border rounded p-2 mb-2"):
                    # File icon and name
                    with ui.row().classes("items-center space-x-2"):
                        ui.icon(self.get_file_icon(file_attachment.file_type)).classes("w-5 h-5")
                        ui.label(file_attachment.filename).classes("font-medium text-sm")
                    
                    # File details
                    with ui.row().classes("items-center justify-between mt-1"):
                        ui.label(format_file_size(file_attachment.file_size)).classes("text-xs opacity-70")
                        
                        # Download button
                        if file_attachment.url:
                            ui.button(
                                "Herunterladen",
                                icon="download",
                                on_click=lambda url=file_attachment.url: self.download_file(url)
                            ).classes("text-xs bg-blue-500 text-white px-2 py-1")
    
    def create_tool_content(self):
        """Create tool message content."""
        if not self.message.tool_results:
            return
        
        with self.content_container:
            for tool_result in self.message.tool_results:
                with ui.element("div").classes("border rounded p-3 mb-2"):
                    # Tool header
                    with ui.row().classes("items-center justify-between mb-2"):
                        with ui.row().classes("items-center space-x-2"):
                            ui.icon("build").classes("w-4 h-4")
                            ui.label(tool_result.tool_name).classes("font-medium text-sm")
                        
                        # Status indicator
                        status_color = "text-green-600" if tool_result.status == "success" else "text-red-600"
                        ui.label(tool_result.status.title()).classes(f"text-xs {status_color}")
                    
                    # Execution time
                    ui.label(f"Ausführungszeit: {tool_result.execution_time:.2f}s").classes("text-xs opacity-70 mb-2")
                    
                    # Tool output
                    if tool_result.status == "success":
                        self.create_tool_output(tool_result.output_data)
                    else:
                        ui.label(f"Fehler: {tool_result.error_message}").classes("text-sm text-red-600")
    
    def create_tool_output(self, output_data: Dict[str, Any]):
        """Create tool output display."""
        if isinstance(output_data, dict):
            with ui.element("div").classes("bg-gray-50 rounded p-2"):
                for key, value in output_data.items():
                    with ui.row().classes("items-start space-x-2"):
                        ui.label(f"{key}:").classes("text-xs font-medium min-w-16")
                        ui.label(str(value)).classes("text-xs flex-1")
        else:
            ui.label(str(output_data)).classes("text-sm")
    
    def create_system_content(self):
        """Create system message content."""
        with self.content_container:
            with ui.row().classes("items-center space-x-2 mb-1"):
                ui.icon("info").classes("w-4 h-4")
                ui.label("System").classes("text-xs font-medium")
            
            ui.label(self.message.content).classes("text-sm")
    
    def create_error_content(self):
        """Create error message content."""
        with self.content_container:
            with ui.row().classes("items-center space-x-2 mb-1"):
                ui.icon("error").classes("w-4 h-4 text-red-500")
                ui.label("Fehler").classes("text-xs font-medium text-red-600")
            
            ui.label(self.message.content).classes("text-sm")
            
            # Show error details if available
            if self.message.metadata and self.message.metadata.get("error_details"):
                with ui.expansion("Details anzeigen").classes("mt-2"):
                    ui.label(str(self.message.metadata["error_details"])).classes("text-xs")
    
    def create_typing_content(self):
        """Create typing indicator content."""
        with self.content_container:
            with ui.row().classes("items-center space-x-2"):
                ui.spinner("dots").classes("w-4 h-4")
                ui.label("Schreibt...").classes("text-sm")
    
    def create_message_metadata(self):
        """Create message metadata display."""
        with self.metadata_container:
            with ui.row().classes("items-center justify-between"):
                # Timestamp
                ui.label(format_relative_time(self.message.timestamp)).classes(
                    "text-xs",
                    "text-blue-200" if self.message.role == "user" else "text-gray-500"
                )
                
                # Status indicator
                if self.message.status != MessageStatus.SENT:
                    status_text = {
                        MessageStatus.SENDING: "Wird gesendet...",
                        MessageStatus.PROCESSING: "Wird verarbeitet...",
                        MessageStatus.FAILED: "Fehler",
                        MessageStatus.DELIVERED: "Zugestellt",
                        MessageStatus.READ: "Gelesen"
                    }.get(self.message.status, "")
                    
                    if status_text:
                        ui.label(status_text).classes(
                            "text-xs",
                            "text-blue-200" if self.message.role == "user" else "text-gray-500"
                        )
                
                # Action buttons
                if self.message.role == "user" and self.message.message_type == MessageType.TEXT:
                    with ui.row().classes("space-x-1"):
                        ui.button(
                            icon="edit",
                            on_click=lambda: self.edit_message()
                        ).classes("w-6 h-6 bg-blue-500 text-white text-xs")
                        
                        ui.button(
                            icon="delete",
                            on_click=lambda: self.delete_message()
                        ).classes("w-6 h-6 bg-red-500 text-white text-xs")
    
    def get_file_icon(self, file_type: str) -> str:
        """Get appropriate icon for file type."""
        if file_type.startswith("image/"):
            return "image"
        elif file_type.startswith("video/"):
            return "video_file"
        elif file_type.startswith("audio/"):
            return "audio_file"
        elif file_type in ["application/pdf"]:
            return "picture_as_pdf"
        elif file_type in ["text/plain", "text/markdown", "text/html"]:
            return "description"
        elif file_type in ["application/json", "application/xml"]:
            return "code"
        else:
            return "attach_file"
    
    def download_file(self, url: str):
        """Download file from URL."""
        # This would need to be implemented based on your file handling
        ui.notify(f"Downloading file from {url}", type="info")
    
    def edit_message(self):
        """Edit the message."""
        # This would trigger an edit dialog
        ui.notify("Edit message functionality", type="info")
    
    def delete_message(self):
        """Delete the message."""
        # This would trigger a delete confirmation
        ui.notify("Delete message functionality", type="info")
    
    def update_status(self, status: MessageStatus):
        """Update message status."""
        self.message.status = status
        # Recreate metadata to reflect new status
        if self.metadata_container:
            self.metadata_container.clear()
            self.create_message_metadata()


def create_message_bubble(message: AdvancedMessage) -> MessageBubble:
    """
    Create a message bubble component.
    
    Args:
        message: Message to display
        
    Returns:
        MessageBubble instance
    """
    return MessageBubble(message)


def create_text_message_bubble(content: str, is_user: bool = True, timestamp: Optional[datetime] = None) -> MessageBubble:
    """
    Create a simple text message bubble.
    
    Args:
        content: Message content
        is_user: Whether message is from user
        timestamp: Message timestamp
        
    Returns:
        MessageBubble instance
    """
    from services.message_service import AdvancedMessage, MessageType, MessageStatus
    
    message = AdvancedMessage(
        id="temp_" + str(hash(content)),
        conversation_id="",
        content=content,
        role="user" if is_user else "assistant",
        message_type=MessageType.TEXT,
        status=MessageStatus.SENT,
        timestamp=timestamp or datetime.now()
    )
    
    return MessageBubble(message)


def create_file_message_bubble(filename: str, file_type: str, file_size: int, url: Optional[str] = None) -> MessageBubble:
    """
    Create a file message bubble.
    
    Args:
        filename: Name of the file
        file_type: MIME type of the file
        file_size: Size of the file in bytes
        url: Download URL for the file
        
    Returns:
        MessageBubble instance
    """
    from services.message_service import AdvancedMessage, MessageType, MessageStatus, FileAttachment
    
    file_attachment = FileAttachment(
        id="temp_file_" + str(hash(filename)),
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        url=url
    )
    
    message = AdvancedMessage(
        id="temp_msg_" + str(hash(filename)),
        conversation_id="",
        content=f"Datei: {filename}",
        role="user",
        message_type=MessageType.FILE,
        status=MessageStatus.SENT,
        timestamp=datetime.now(),
        file_attachments=[file_attachment]
    )
    
    return MessageBubble(message)


def create_tool_message_bubble(tool_result: ToolExecutionResult) -> MessageBubble:
    """
    Create a tool message bubble.
    
    Args:
        tool_result: Tool execution result
        
    Returns:
        MessageBubble instance
    """
    from services.message_service import AdvancedMessage, MessageType, MessageStatus, ToolResult
    
    tool_result_obj = ToolResult(
        tool_name=tool_result.tool_name,
        tool_id=tool_result.tool_id,
        input_data=tool_result.input_data,
        output_data=tool_result.output_data,
        execution_time=tool_result.execution_time,
        status=tool_result.status,
        error_message=tool_result.error_message
    )
    
    message = AdvancedMessage(
        id="temp_tool_" + str(hash(tool_result.tool_id)),
        conversation_id="",
        content=f"Tool '{tool_result.tool_name}' ausgeführt",
        role="assistant",
        message_type=MessageType.TOOL,
        status=MessageStatus.SENT,
        timestamp=datetime.now(),
        tool_results=[tool_result_obj]
    )
    
    return MessageBubble(message) 