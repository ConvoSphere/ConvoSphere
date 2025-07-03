"""
Conversation service for the AI Assistant Platform.

This module provides conversation management functionality including
CRUD operations, message handling, and conversation history.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .api import api_client
from .error_handler import handle_api_error, handle_network_error
from utils.helpers import generate_id, format_timestamp, format_relative_time


@dataclass
class Message:
    """Message data model."""
    id: str
    conversation_id: str
    content: str
    role: str  # user, assistant, system
    message_type: str  # text, tool, file, error
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    is_loading: bool = False


@dataclass
class Conversation:
    """Conversation data model."""
    id: str
    title: str
    assistant_id: str
    assistant_name: str
    status: str  # active, archived, deleted
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None


class ConversationService:
    """Service for managing conversations."""
    
    def __init__(self):
        """Initialize the conversation service."""
        self.conversations: List[Conversation] = []
        self.current_conversation: Optional[Conversation] = None
        self.messages: Dict[str, List[Message]] = {}  # conversation_id -> messages
        self.is_loading = False
    
    async def get_conversations(self, force_refresh: bool = False) -> List[Conversation]:
        """
        Get all conversations.
        
        Args:
            force_refresh: Force refresh from API
            
        Returns:
            List of conversations
        """
        if not force_refresh and self.conversations:
            return self.conversations
        
        self.is_loading = True
        
        try:
            response = await api_client.get_conversations()
            
            if response.success and response.data:
                self.conversations = []
                for conv_data in response.data:
                    conversation = self._create_conversation_from_data(conv_data)
                    self.conversations.append(conversation)
                
                # Sort by updated_at (newest first)
                self.conversations.sort(key=lambda x: x.updated_at, reverse=True)
                
                return self.conversations
            else:
                handle_api_error(response, "Laden der Konversationen")
                return []
                
        except Exception as e:
            handle_network_error(e, "Laden der Konversationen")
            return []
        finally:
            self.is_loading = False
    
    async def create_conversation(self, assistant_id: str, title: Optional[str] = None) -> Optional[Conversation]:
        """
        Create new conversation.
        
        Args:
            assistant_id: Assistant ID
            title: Optional conversation title
            
        Returns:
            Created conversation or None if failed
        """
        try:
            # Get assistant name for title
            assistant_name = "Unknown Assistant"
            if not title:
                # Try to get assistant name from assistant service
                try:
                    from .assistant_service import assistant_service
                    assistant = assistant_service.get_assistant_by_name(assistant_id)
                    if assistant:
                        assistant_name = assistant.name
                        title = f"Neue Konversation mit {assistant_name}"
                    else:
                        title = "Neue Konversation"
                except:
                    title = "Neue Konversation"
            
            response = await api_client.create_conversation(assistant_id, title)
            
            if response.success and response.data:
                conversation = self._create_conversation_from_data(response.data)
                self.conversations.insert(0, conversation)  # Add to beginning
                self.messages[conversation.id] = []
                return conversation
            else:
                handle_api_error(response, "Erstellen der Konversation")
                return None
                
        except Exception as e:
            handle_network_error(e, "Erstellen der Konversation")
            return None
    
    async def get_conversation_messages(self, conversation_id: str, force_refresh: bool = False) -> List[Message]:
        """
        Get messages for a conversation.
        
        Args:
            conversation_id: Conversation ID
            force_refresh: Force refresh from API
            
        Returns:
            List of messages
        """
        if not force_refresh and conversation_id in self.messages:
            return self.messages[conversation_id]
        
        try:
            response = await api_client.get_conversation_messages(conversation_id)
            
            if response.success and response.data:
                messages = []
                for msg_data in response.data:
                    message = self._create_message_from_data(msg_data)
                    messages.append(message)
                
                self.messages[conversation_id] = messages
                return messages
            else:
                handle_api_error(response, f"Laden der Nachrichten für Konversation {conversation_id}")
                return []
                
        except Exception as e:
            handle_network_error(e, f"Laden der Nachrichten für Konversation {conversation_id}")
            return []
    
    async def send_message(self, conversation_id: str, content: str) -> Optional[Message]:
        """
        Send message to conversation.
        
        Args:
            conversation_id: Conversation ID
            content: Message content
            
        Returns:
            Sent message or None if failed
        """
        try:
            # Create temporary message for immediate display
            temp_message = Message(
                id=generate_id("msg_"),
                conversation_id=conversation_id,
                content=content,
                role="user",
                message_type="text",
                timestamp=datetime.now(),
                is_loading=False
            )
            
            # Add to local messages
            if conversation_id not in self.messages:
                self.messages[conversation_id] = []
            self.messages[conversation_id].append(temp_message)
            
            # Send to API
            response = await api_client.send_message(conversation_id, content)
            
            if response.success and response.data:
                # Replace temp message with real one
                real_message = self._create_message_from_data(response.data)
                
                # Update in local messages
                for i, msg in enumerate(self.messages[conversation_id]):
                    if msg.id == temp_message.id:
                        self.messages[conversation_id][i] = real_message
                        break
                
                # Update conversation
                await self._update_conversation_after_message(conversation_id, real_message)
                
                return real_message
            else:
                # Remove temp message on failure
                self.messages[conversation_id] = [msg for msg in self.messages[conversation_id] if msg.id != temp_message.id]
                handle_api_error(response, "Senden der Nachricht")
                return None
                
        except Exception as e:
            handle_network_error(e, "Senden der Nachricht")
            return None
    
    async def archive_conversation(self, conversation_id: str) -> bool:
        """
        Archive conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update local conversation status
            for conversation in self.conversations:
                if conversation.id == conversation_id:
                    conversation.status = "archived"
                    break
            
            # TODO: Implement API call for archiving
            # response = await api_client.archive_conversation(conversation_id)
            
            return True
        except Exception as e:
            handle_network_error(e, f"Archivieren der Konversation {conversation_id}")
            return False
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from local lists
            self.conversations = [c for c in self.conversations if c.id != conversation_id]
            
            if conversation_id in self.messages:
                del self.messages[conversation_id]
            
            # Clear current conversation if it's the same
            if self.current_conversation and self.current_conversation.id == conversation_id:
                self.current_conversation = None
            
            # TODO: Implement API call for deletion
            # response = await api_client.delete_conversation(conversation_id)
            
            return True
        except Exception as e:
            handle_network_error(e, f"Löschen der Konversation {conversation_id}")
            return False
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation or None if not found
        """
        for conversation in self.conversations:
            if conversation.id == conversation_id:
                return conversation
        return None
    
    def search_conversations(self, query: str) -> List[Conversation]:
        """
        Search conversations by title or content.
        
        Args:
            query: Search query
            
        Returns:
            List of matching conversations
        """
        query_lower = query.lower()
        matching_conversations = []
        
        for conversation in self.conversations:
            # Check title
            if query_lower in conversation.title.lower():
                matching_conversations.append(conversation)
                continue
            
            # Check last message
            if conversation.last_message and query_lower in conversation.last_message.lower():
                matching_conversations.append(conversation)
                continue
            
            # Check messages in conversation
            if conversation.id in self.messages:
                for message in self.messages[conversation.id]:
                    if query_lower in message.content.lower():
                        matching_conversations.append(conversation)
                        break
        
        return matching_conversations
    
    def get_active_conversations(self) -> List[Conversation]:
        """
        Get only active conversations.
        
        Returns:
            List of active conversations
        """
        return [c for c in self.conversations if c.status == "active"]
    
    def get_archived_conversations(self) -> List[Conversation]:
        """
        Get only archived conversations.
        
        Returns:
            List of archived conversations
        """
        return [c for c in self.conversations if c.status == "archived"]
    
    async def _update_conversation_after_message(self, conversation_id: str, message: Message):
        """
        Update conversation after new message.
        
        Args:
            conversation_id: Conversation ID
            message: New message
        """
        for conversation in self.conversations:
            if conversation.id == conversation_id:
                conversation.updated_at = message.timestamp
                conversation.last_message = message.content
                conversation.last_message_time = message.timestamp
                conversation.message_count = len(self.messages.get(conversation_id, []))
                
                # Move to top of list
                self.conversations.remove(conversation)
                self.conversations.insert(0, conversation)
                break
    
    def _create_conversation_from_data(self, data: Dict[str, Any]) -> Conversation:
        """
        Create Conversation object from API data.
        
        Args:
            data: API response data
            
        Returns:
            Conversation object
        """
        return Conversation(
            id=data.get("id", generate_id("conv_")),
            title=data.get("title", "Neue Konversation"),
            assistant_id=data.get("assistant_id", ""),
            assistant_name=data.get("assistant_name", "Unknown Assistant"),
            status=data.get("status", "active"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            message_count=data.get("message_count", 0),
            last_message=data.get("last_message"),
            last_message_time=datetime.fromisoformat(data["last_message_time"]) if data.get("last_message_time") else None
        )
    
    def _create_message_from_data(self, data: Dict[str, Any]) -> Message:
        """
        Create Message object from API data.
        
        Args:
            data: API response data
            
        Returns:
            Message object
        """
        return Message(
            id=data.get("id", generate_id("msg_")),
            conversation_id=data.get("conversation_id", ""),
            content=data.get("content", ""),
            role=data.get("role", "user"),
            message_type=data.get("message_type", "text"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            metadata=data.get("metadata"),
            tool_results=data.get("tool_results"),
            is_loading=False
        )
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Get conversation statistics.
        
        Returns:
            Dictionary with statistics
        """
        total = len(self.conversations)
        active = len(self.get_active_conversations())
        archived = len(self.get_archived_conversations())
        
        total_messages = sum(len(messages) for messages in self.messages.values())
        
        return {
            "total_conversations": total,
            "active_conversations": active,
            "archived_conversations": archived,
            "total_messages": total_messages,
            "average_messages_per_conversation": total_messages / total if total > 0 else 0
        }


# Global conversation service instance
conversation_service = ConversationService() 