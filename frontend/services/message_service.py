"""
Message service for the AI Assistant Platform.

This module provides advanced message handling functionality including
different message types, file uploads, tool execution, and message formatting.
"""

import asyncio
import base64
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum

from .api import api_client
from .error_handler import handle_api_error, handle_network_error
from utils.helpers import generate_id, format_timestamp
from utils.validators import validate_message_data, sanitize_input


class MessageType(Enum):
    """Message types enumeration."""
    TEXT = "text"
    FILE = "file"
    TOOL = "tool"
    SYSTEM = "system"
    ERROR = "error"
    TYPING = "typing"


class MessageStatus(Enum):
    """Message status enumeration."""
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    PROCESSING = "processing"


@dataclass
class FileAttachment:
    """File attachment data model."""
    id: str
    filename: str
    file_type: str
    file_size: int
    url: Optional[str] = None
    content: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ToolResult:
    """Tool execution result data model."""
    tool_name: str
    tool_id: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time: float
    status: str  # success, error, timeout
    error_message: Optional[str] = None


@dataclass
class AdvancedMessage:
    """Advanced message data model with support for different types."""
    id: str
    conversation_id: str
    content: str
    role: str  # user, assistant, system
    message_type: MessageType
    status: MessageStatus
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    file_attachments: Optional[List[FileAttachment]] = None
    tool_results: Optional[List[ToolResult]] = None
    reply_to: Optional[str] = None
    is_edited: bool = False
    edit_history: Optional[List[Dict[str, Any]]] = None


class MessageService:
    """Service for advanced message handling."""
    
    def __init__(self):
        """Initialize the message service."""
        self.message_queue: List[AdvancedMessage] = []
        self.processing_messages: Dict[str, AdvancedMessage] = {}
        self.file_cache: Dict[str, FileAttachment] = {}
    
    async def send_text_message(
        self,
        conversation_id: str,
        content: str,
        reply_to: Optional[str] = None
    ) -> Optional[AdvancedMessage]:
        """
        Send a text message.
        
        Args:
            conversation_id: Conversation ID
            content: Message content
            reply_to: ID of message to reply to
            
        Returns:
            Sent message or None if failed
        """
        try:
            # Validate message data
            message_data = {
                "content": content,
                "conversation_id": conversation_id
            }
            validation = validate_message_data(message_data)
            if not validation["valid"]:
                raise ValueError(f"Message validation failed: {validation['errors']}")
            
            # Sanitize content
            sanitized_content = sanitize_input(content, max_length=10000)
            
            # Create message object
            message = AdvancedMessage(
                id=generate_id("msg_"),
                conversation_id=conversation_id,
                content=sanitized_content,
                role="user",
                message_type=MessageType.TEXT,
                status=MessageStatus.SENDING,
                timestamp=datetime.now(),
                reply_to=reply_to
            )
            
            # Add to processing queue
            self.processing_messages[message.id] = message
            
            # Send to API
            response = await api_client.send_message(conversation_id, sanitized_content)
            
            if response.success and response.data:
                # Update message with API response
                message.id = response.data.get("id", message.id)
                message.status = MessageStatus.SENT
                message.timestamp = datetime.fromisoformat(response.data["timestamp"]) if response.data.get("timestamp") else datetime.now()
                
                # Remove from processing
                if message.id in self.processing_messages:
                    del self.processing_messages[message.id]
                
                return message
            else:
                # Mark as failed
                message.status = MessageStatus.FAILED
                handle_api_error(response, "Senden der Nachricht")
                return None
                
        except Exception as e:
            handle_network_error(e, "Senden der Nachricht")
            return None
    
    async def send_file_message(
        self,
        conversation_id: str,
        file_data: bytes,
        filename: str,
        file_type: str,
        reply_to: Optional[str] = None
    ) -> Optional[AdvancedMessage]:
        """
        Send a file message.
        
        Args:
            conversation_id: Conversation ID
            file_data: File content as bytes
            filename: Name of the file
            file_type: MIME type of the file
            reply_to: ID of message to reply to
            
        Returns:
            Sent message or None if failed
        """
        try:
            # Create file attachment
            file_attachment = FileAttachment(
                id=generate_id("file_"),
                filename=filename,
                file_type=file_type,
                file_size=len(file_data),
                content=file_data
            )
            
            # Create message
            message = AdvancedMessage(
                id=generate_id("msg_"),
                conversation_id=conversation_id,
                content=f"Datei: {filename}",
                role="user",
                message_type=MessageType.FILE,
                status=MessageStatus.SENDING,
                timestamp=datetime.now(),
                file_attachments=[file_attachment],
                reply_to=reply_to
            )
            
            # Add to processing queue
            self.processing_messages[message.id] = message
            
            # Upload file to API
            response = await api_client.upload_file(
                conversation_id,
                file_data,
                filename,
                file_type
            )
            
            if response.success and response.data:
                # Update message with API response
                message.id = response.data.get("id", message.id)
                message.status = MessageStatus.SENT
                message.timestamp = datetime.fromisoformat(response.data["timestamp"]) if response.data.get("timestamp") else datetime.now()
                
                # Update file attachment with URL
                if response.data.get("file_url"):
                    file_attachment.url = response.data["file_url"]
                
                # Cache file
                self.file_cache[file_attachment.id] = file_attachment
                
                # Remove from processing
                if message.id in self.processing_messages:
                    del self.processing_messages[message.id]
                
                return message
            else:
                # Mark as failed
                message.status = MessageStatus.FAILED
                handle_api_error(response, "Hochladen der Datei")
                return None
                
        except Exception as e:
            handle_network_error(e, "Hochladen der Datei")
            return None
    
    async def execute_tool(
        self,
        conversation_id: str,
        tool_id: str,
        tool_input: Dict[str, Any],
        reply_to: Optional[str] = None
    ) -> Optional[AdvancedMessage]:
        """
        Execute a tool and send the result as a message.
        
        Args:
            conversation_id: Conversation ID
            tool_id: Tool ID to execute
            tool_input: Input data for the tool
            reply_to: ID of message to reply to
            
        Returns:
            Message with tool result or None if failed
        """
        try:
            # Create message for tool execution
            message = AdvancedMessage(
                id=generate_id("msg_"),
                conversation_id=conversation_id,
                content=f"Führe Tool aus: {tool_id}",
                role="assistant",
                message_type=MessageType.TOOL,
                status=MessageStatus.PROCESSING,
                timestamp=datetime.now(),
                reply_to=reply_to
            )
            
            # Add to processing queue
            self.processing_messages[message.id] = message
            
            # Execute tool
            start_time = datetime.now()
            response = await api_client.execute_tool(tool_id, tool_input)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if response.success and response.data:
                # Create tool result
                tool_result = ToolResult(
                    tool_name=response.data.get("tool_name", tool_id),
                    tool_id=tool_id,
                    input_data=tool_input,
                    output_data=response.data.get("result", {}),
                    execution_time=execution_time,
                    status="success"
                )
                
                # Update message
                message.content = f"Tool '{tool_result.tool_name}' erfolgreich ausgeführt"
                message.status = MessageStatus.SENT
                message.tool_results = [tool_result]
                message.timestamp = datetime.now()
                
                # Remove from processing
                if message.id in self.processing_messages:
                    del self.processing_messages[message.id]
                
                return message
            else:
                # Create error tool result
                tool_result = ToolResult(
                    tool_name=tool_id,
                    tool_id=tool_id,
                    input_data=tool_input,
                    output_data={},
                    execution_time=execution_time,
                    status="error",
                    error_message=response.error if hasattr(response, 'error') else "Unknown error"
                )
                
                # Update message
                message.content = f"Fehler bei Tool-Ausführung: {tool_result.error_message}"
                message.status = MessageStatus.FAILED
                message.tool_results = [tool_result]
                message.timestamp = datetime.now()
                
                # Remove from processing
                if message.id in self.processing_messages:
                    del self.processing_messages[message.id]
                
                return message
                
        except Exception as e:
            handle_network_error(e, "Tool-Ausführung")
            return None
    
    async def edit_message(
        self,
        message_id: str,
        new_content: str
    ) -> Optional[AdvancedMessage]:
        """
        Edit an existing message.
        
        Args:
            message_id: Message ID to edit
            new_content: New message content
            
        Returns:
            Updated message or None if failed
        """
        try:
            # Validate new content
            validation = validate_message_data({"content": new_content})
            if not validation["valid"]:
                raise ValueError(f"Message validation failed: {validation['errors']}")
            
            # Sanitize content
            sanitized_content = sanitize_input(new_content, max_length=10000)
            
            # Send edit request to API
            response = await api_client.edit_message(message_id, sanitized_content)
            
            if response.success and response.data:
                # Create updated message
                message = AdvancedMessage(
                    id=message_id,
                    conversation_id=response.data.get("conversation_id", ""),
                    content=sanitized_content,
                    role=response.data.get("role", "user"),
                    message_type=MessageType.TEXT,
                    status=MessageStatus.SENT,
                    timestamp=datetime.fromisoformat(response.data["timestamp"]) if response.data.get("timestamp") else datetime.now(),
                    is_edited=True,
                    edit_history=response.data.get("edit_history", [])
                )
                
                return message
            else:
                handle_api_error(response, "Bearbeiten der Nachricht")
                return None
                
        except Exception as e:
            handle_network_error(e, "Bearbeiten der Nachricht")
            return None
    
    async def delete_message(self, message_id: str) -> bool:
        """
        Delete a message.
        
        Args:
            message_id: Message ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client.delete_message(message_id)
            
            if response.success:
                return True
            else:
                handle_api_error(response, "Löschen der Nachricht")
                return False
                
        except Exception as e:
            handle_network_error(e, "Löschen der Nachricht")
            return False
    
    def create_typing_indicator(self, conversation_id: str) -> AdvancedMessage:
        """
        Create a typing indicator message.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Typing indicator message
        """
        return AdvancedMessage(
            id=generate_id("typing_"),
            conversation_id=conversation_id,
            content="...",
            role="assistant",
            message_type=MessageType.TYPING,
            status=MessageStatus.PROCESSING,
            timestamp=datetime.now()
        )
    
    def create_system_message(
        self,
        conversation_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AdvancedMessage:
        """
        Create a system message.
        
        Args:
            conversation_id: Conversation ID
            content: System message content
            metadata: Additional metadata
            
        Returns:
            System message
        """
        return AdvancedMessage(
            id=generate_id("sys_"),
            conversation_id=conversation_id,
            content=content,
            role="system",
            message_type=MessageType.SYSTEM,
            status=MessageStatus.SENT,
            timestamp=datetime.now(),
            metadata=metadata
        )
    
    def create_error_message(
        self,
        conversation_id: str,
        error_content: str,
        error_details: Optional[Dict[str, Any]] = None
    ) -> AdvancedMessage:
        """
        Create an error message.
        
        Args:
            conversation_id: Conversation ID
            error_content: Error message content
            error_details: Additional error details
            
        Returns:
            Error message
        """
        return AdvancedMessage(
            id=generate_id("error_"),
            conversation_id=conversation_id,
            content=error_content,
            role="system",
            message_type=MessageType.ERROR,
            status=MessageStatus.FAILED,
            timestamp=datetime.now(),
            metadata={"error_details": error_details}
        )
    
    def get_processing_messages(self) -> List[AdvancedMessage]:
        """
        Get all currently processing messages.
        
        Returns:
            List of processing messages
        """
        return list(self.processing_messages.values())
    
    def get_file_attachment(self, file_id: str) -> Optional[FileAttachment]:
        """
        Get a cached file attachment.
        
        Args:
            file_id: File ID
            
        Returns:
            File attachment or None if not found
        """
        return self.file_cache.get(file_id)
    
    def clear_file_cache(self):
        """Clear the file cache."""
        self.file_cache.clear()
    
    def format_message_for_display(self, message: AdvancedMessage) -> Dict[str, Any]:
        """
        Format a message for display in the UI.
        
        Args:
            message: Message to format
            
        Returns:
            Formatted message data
        """
        formatted = {
            "id": message.id,
            "content": message.content,
            "role": message.role,
            "type": message.message_type.value,
            "status": message.status.value,
            "timestamp": format_timestamp(message.timestamp),
            "is_edited": message.is_edited,
            "reply_to": message.reply_to
        }
        
        # Add file attachments
        if message.file_attachments:
            formatted["files"] = [
                {
                    "id": file.id,
                    "filename": file.filename,
                    "type": file.file_type,
                    "size": file.file_size,
                    "url": file.url
                }
                for file in message.file_attachments
            ]
        
        # Add tool results
        if message.tool_results:
            formatted["tools"] = [
                {
                    "name": tool.tool_name,
                    "id": tool.tool_id,
                    "status": tool.status,
                    "execution_time": tool.execution_time,
                    "output": tool.output_data,
                    "error": tool.error_message
                }
                for tool in message.tool_results
            ]
        
        # Add metadata
        if message.metadata:
            formatted["metadata"] = message.metadata
        
        return formatted


# Global message service instance
message_service = MessageService() 