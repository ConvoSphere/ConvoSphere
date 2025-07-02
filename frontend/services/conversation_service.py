"""
Conversation service for the frontend.

This module provides conversation management and chat state handling.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """Message data model."""
    id: str
    content: str
    role: str  # "user" or "assistant"
    message_type: str = "text"
    timestamp: str = ""
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None


@dataclass
class Conversation:
    """Conversation data model."""
    id: str
    title: str
    description: Optional[str] = None
    user_id: str = ""
    assistant_id: str = ""
    is_active: bool = True
    is_archived: bool = False
    message_count: int = 0
    total_tokens: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ConversationService:
    """Conversation service for managing chat conversations."""
    
    def __init__(self):
        self.conversations: List[Conversation] = []
        self.current_conversation: Optional[Conversation] = None
        self.current_messages: List[Message] = []
    
    def set_conversations(self, conversations_data: List[Dict[str, Any]]) -> None:
        """
        Set conversations from API data.
        
        Args:
            conversations_data: List of conversation data from API
        """
        self.conversations = [
            Conversation(**conversation_data) for conversation_data in conversations_data
        ]
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Optional[Conversation]: Conversation if found
        """
        for conversation in self.conversations:
            if conversation.id == conversation_id:
                return conversation
        return None
    
    def get_active_conversations(self) -> List[Conversation]:
        """
        Get active conversations.
        
        Returns:
            List[Conversation]: List of active conversations
        """
        return [c for c in self.conversations if c.is_active and not c.is_archived]
    
    def get_archived_conversations(self) -> List[Conversation]:
        """
        Get archived conversations.
        
        Returns:
            List[Conversation]: List of archived conversations
        """
        return [c for c in self.conversations if c.is_archived]
    
    def set_current_conversation(self, conversation: Conversation) -> None:
        """
        Set current conversation.
        
        Args:
            conversation: Conversation to set as current
        """
        self.current_conversation = conversation
        self.current_messages = []  # Clear messages, will be loaded separately
    
    def get_current_conversation(self) -> Optional[Conversation]:
        """
        Get current conversation.
        
        Returns:
            Optional[Conversation]: Current conversation
        """
        return self.current_conversation
    
    def set_messages(self, messages_data: List[Dict[str, Any]]) -> None:
        """
        Set messages for current conversation.
        
        Args:
            messages_data: List of message data from API
        """
        self.current_messages = [
            Message(**message_data) for message_data in messages_data
        ]
    
    def get_messages(self) -> List[Message]:
        """
        Get current conversation messages.
        
        Returns:
            List[Message]: List of messages
        """
        return self.current_messages
    
    def add_message(self, message: Message) -> None:
        """
        Add message to current conversation.
        
        Args:
            message: Message to add
        """
        self.current_messages.append(message)
        
        # Update conversation message count
        if self.current_conversation:
            self.current_conversation.message_count += 1
            if message.tokens_used:
                self.current_conversation.total_tokens += message.tokens_used
    
    def add_user_message(self, content: str) -> Message:
        """
        Add user message to current conversation.
        
        Args:
            content: Message content
            
        Returns:
            Message: Created message
        """
        message = Message(
            id=f"user_{len(self.current_messages)}",
            content=content,
            role="user",
            message_type="text",
            timestamp=datetime.now().isoformat()
        )
        self.add_message(message)
        return message
    
    def add_assistant_message(
        self,
        content: str,
        tokens_used: Optional[int] = None,
        model_used: Optional[str] = None
    ) -> Message:
        """
        Add assistant message to current conversation.
        
        Args:
            content: Message content
            tokens_used: Number of tokens used
            model_used: Model used for response
            
        Returns:
            Message: Created message
        """
        message = Message(
            id=f"assistant_{len(self.current_messages)}",
            content=content,
            role="assistant",
            message_type="text",
            timestamp=datetime.now().isoformat(),
            tokens_used=tokens_used,
            model_used=model_used
        )
        self.add_message(message)
        return message
    
    def clear_messages(self) -> None:
        """Clear current conversation messages."""
        self.current_messages = []
    
    def add_conversation(self, conversation: Conversation) -> None:
        """
        Add conversation to list.
        
        Args:
            conversation: Conversation to add
        """
        self.conversations.append(conversation)
    
    def remove_conversation(self, conversation_id: str) -> None:
        """
        Remove conversation from list.
        
        Args:
            conversation_id: Conversation ID to remove
        """
        self.conversations = [c for c in self.conversations if c.id != conversation_id]
        
        # Clear current conversation if it was removed
        if self.current_conversation and self.current_conversation.id == conversation_id:
            self.current_conversation = None
            self.current_messages = []
    
    def update_conversation(self, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update conversation data.
        
        Args:
            conversation_id: Conversation ID to update
            updates: Updates to apply
            
        Returns:
            bool: True if updated successfully
        """
        for conversation in self.conversations:
            if conversation.id == conversation_id:
                for key, value in updates.items():
                    if hasattr(conversation, key):
                        setattr(conversation, key, value)
                
                # Update current conversation if it was updated
                if self.current_conversation and self.current_conversation.id == conversation_id:
                    self.current_conversation = conversation
                
                return True
        
        return False
    
    def get_conversation_title(self, conversation: Conversation) -> str:
        """
        Get conversation title or generate one.
        
        Args:
            conversation: Conversation object
            
        Returns:
            str: Conversation title
        """
        if conversation.title and conversation.title != "New Conversation":
            return conversation.title
        
        # Generate title from first message
        if self.current_messages:
            first_message = self.current_messages[0]
            if first_message.role == "user":
                title = first_message.content[:50]
                if len(first_message.content) > 50:
                    title += "..."
                return title
        
        return "New Conversation"


# Global conversation service instance
conversation_service = ConversationService() 