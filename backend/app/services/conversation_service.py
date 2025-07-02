"""Conversation service for managing chat conversations."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid
from datetime import datetime

from app.models.conversation import Conversation, Message, MessageRole, MessageType
from app.models.assistant import Assistant
from app.models.user import User


class ConversationService:
    """Service for managing conversations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_conversation(
        self,
        user_id: str,
        assistant_id: str,
        title: str = "New Conversation"
    ) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            user_id: User ID
            assistant_id: Assistant ID
            title: Conversation title
            
        Returns:
            Dict[str, Any]: Created conversation data
        """
        conversation = Conversation(
            user_id=user_id,
            assistant_id=assistant_id,
            title=title,
            is_active=True
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation.to_dict()
    
    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation by ID and verify ownership.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID for verification
            
        Returns:
            Optional[Dict[str, Any]]: Conversation data if found and owned
        """
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        return conversation.to_dict() if conversation else None
    
    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[Dict[str, Any]]: List of conversations
        """
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(desc(Conversation.updated_at)).all()
        
        return [conv.to_dict() for conv in conversations]
    
    def add_message(
        self,
        conversation_id: str,
        user_id: Optional[str],
        content: str,
        role: MessageRole,
        message_type: MessageType = MessageType.TEXT,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (None for assistant messages)
            content: Message content
            role: Message role
            message_type: Message type
            metadata: Additional metadata
            
        Returns:
            Dict[str, Any]: Created message data
        """
        message = Message(
            conversation_id=conversation_id,
            content=content,
            role=role,
            message_type=message_type,
            metadata=metadata or {}
        )
        
        # Set token usage if provided
        if metadata and "tokens_used" in metadata:
            message.tokens_used = metadata["tokens_used"]
        
        if metadata and "model_used" in metadata:
            message.model_used = metadata["model_used"]
        
        self.db.add(message)
        
        # Update conversation message count
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if conversation:
            conversation.message_count += 1
            if message.tokens_used:
                conversation.total_tokens += message.tokens_used
        
        self.db.commit()
        self.db.refresh(message)
        
        return message.to_dict()
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages in a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List[Dict[str, Any]]: List of messages
        """
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        return [msg.to_dict() for msg in messages]
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history for AI context.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List[Dict[str, str]]: List of messages in LiteLLM format
        """
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        # Convert to LiteLLM format
        history = []
        for msg in messages:
            if msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                history.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        return history
    
    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID for verification
            
        Returns:
            bool: True if deleted, False otherwise
        """
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return False
        
        self.db.delete(conversation)
        self.db.commit()
        
        return True
    
    def archive_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Archive a conversation.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID for verification
            
        Returns:
            bool: True if archived, False otherwise
        """
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return False
        
        conversation.is_archived = True
        conversation.is_active = False
        self.db.commit()
        
        return True 