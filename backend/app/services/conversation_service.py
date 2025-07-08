"""Conversation service for managing chat conversations."""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_, func
import json
import os
from datetime import datetime, timedelta
import uuid

from app.models.conversation import Conversation, Message, MessageRole, MessageType, MessageReaction


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
    
    def update_conversation(
        self,
        conversation_id: str,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a conversation.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID for verification
            update_data: Data to update
            
        Returns:
            Optional[Dict[str, Any]]: Updated conversation data
        """
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return None
        
        # Update allowed fields
        for field, value in update_data.items():
            if hasattr(conversation, field):
                setattr(conversation, field, value)
        
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation.to_dict()
    
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
            message_metadata=metadata or {}
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
    
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages in a conversation with pagination.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
            offset: Number of messages to skip
            
        Returns:
            List[Dict[str, Any]]: List of messages
        """
        query = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        messages = query.all()
        return [msg.to_dict() for msg in messages]
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for context management.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of messages in AI format
        """
        try:
            messages = self.get_conversation_messages(
                conversation_id=conversation_id,
                limit=limit
            )
            
            # Convert to AI message format
            ai_messages = []
            for msg in messages:
                ai_message = {
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("created_at"),
                    "message_id": str(msg.get("id")),
                    "metadata": msg.get("metadata", {})
                }
                ai_messages.append(ai_message)
            
            return ai_messages
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """
        Get conversation with user validation.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID for validation
            
        Returns:
            Optional[Conversation]: Conversation if found and accessible
        """
        try:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                return None
            
            # Check if user has access to this conversation
            if conversation.user_id != user_id:
                logger.warning(f"User {user_id} tried to access conversation {conversation_id} without permission")
                return None
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {e}")
            return None
    
    def search_messages(
        self,
        conversation_id: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search messages in a conversation.
        
        Args:
            conversation_id: Conversation ID
            query: Search query
            filters: Additional filters
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: Messages and total count
        """
        # Build search query
        search_query = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        )
        
        # Add text search
        if query:
            search_query = search_query.filter(
                or_(
                    Message.content.ilike(f"%{query}%"),
                    Message.message_metadata.contains({"searchable_text": query})
                )
            )
        
        # Add filters
        if filters:
            if "role" in filters:
                search_query = search_query.filter(Message.role == filters["role"])
            if "message_type" in filters:
                search_query = search_query.filter(Message.message_type == filters["message_type"])
            if "date_from" in filters:
                search_query = search_query.filter(Message.created_at >= filters["date_from"])
            if "date_to" in filters:
                search_query = search_query.filter(Message.created_at <= filters["date_to"])
        
        # Get total count
        total = search_query.count()
        
        # Apply pagination
        messages = search_query.order_by(desc(Message.created_at)).offset(offset).limit(limit).all()
        
        return [msg.to_dict() for msg in messages], total
    
    def delete_message(
        self,
        conversation_id: str,
        message_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a message (only own messages).
        
        Args:
            conversation_id: Conversation ID
            message_id: Message ID
            user_id: User ID for verification
            
        Returns:
            bool: True if deleted, False otherwise
        """
        # Verify conversation ownership
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return False
        
        # Get message and verify it's a user message
        message = self.db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.conversation_id == conversation_id,
                Message.role == MessageRole.USER
            )
        ).first()
        
        if not message:
            return False
        
        # Delete message
        self.db.delete(message)
        
        # Update conversation message count
        conversation.message_count = max(0, conversation.message_count - 1)
        
        self.db.commit()
        return True
    
    def add_message_reaction(
        self,
        conversation_id: str,
        message_id: str,
        user_id: str,
        emoji: str
    ) -> Optional[Dict[str, Any]]:
        """
        Add a reaction to a message.
        
        Args:
            conversation_id: Conversation ID
            message_id: Message ID
            user_id: User ID
            emoji: Emoji reaction
            
        Returns:
            Optional[Dict[str, Any]]: Created reaction data
        """
        # Verify message exists
        message = self.db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.conversation_id == conversation_id
            )
        ).first()
        
        if not message:
            return None
        
        # Check if reaction already exists
        existing_reaction = self.db.query(MessageReaction).filter(
            and_(
                MessageReaction.message_id == message_id,
                MessageReaction.user_id == user_id,
                MessageReaction.emoji == emoji
            )
        ).first()
        
        if existing_reaction:
            return existing_reaction.to_dict()
        
        # Create new reaction
        reaction = MessageReaction(
            message_id=message_id,
            user_id=user_id,
            emoji=emoji
        )
        
        self.db.add(reaction)
        self.db.commit()
        self.db.refresh(reaction)
        
        return reaction.to_dict()
    
    def remove_message_reaction(
        self,
        conversation_id: str,
        message_id: str,
        reaction_id: str,
        user_id: str
    ) -> bool:
        """
        Remove a reaction from a message.
        
        Args:
            conversation_id: Conversation ID
            message_id: Message ID
            reaction_id: Reaction ID
            user_id: User ID for verification
            
        Returns:
            bool: True if removed, False otherwise
        """
        # Verify reaction ownership
        reaction = self.db.query(MessageReaction).filter(
            and_(
                MessageReaction.id == reaction_id,
                MessageReaction.message_id == message_id,
                MessageReaction.user_id == user_id
            )
        ).first()
        
        if not reaction:
            return False
        
        # Remove reaction
        self.db.delete(reaction)
        self.db.commit()
        
        return True
    
    def export_conversation(
        self,
        conversation_id: str,
        format: str,
        include_metadata: bool = True,
        include_attachments: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Export a conversation in various formats.
        
        Args:
            conversation_id: Conversation ID
            format: Export format (json, markdown, pdf, txt)
            include_metadata: Include message metadata
            include_attachments: Include attachments
            
        Returns:
            Optional[Dict[str, Any]]: Export result with download URL
        """
        # Get conversation and messages
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            return None
        
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        # Create export data
        export_data = {
            "conversation": conversation.to_dict(),
            "messages": [msg.to_dict() for msg in messages],
            "export_info": {
                "format": format,
                "exported_at": datetime.utcnow().isoformat(),
                "include_metadata": include_metadata,
                "include_attachments": include_attachments
            }
        }
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{conversation_id}_{timestamp}.{format}"
        
        # Create exports directory if it doesn't exist
        exports_dir = "exports"
        os.makedirs(exports_dir, exist_ok=True)
        
        file_path = os.path.join(exports_dir, filename)
        
        # Export based on format
        if format == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        elif format == "markdown":
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {conversation.title}\n\n")
                f.write(f"**Created:** {conversation.created_at}\n")
                f.write(f"**Assistant:** {conversation.assistant_id}\n\n")
                f.write("---\n\n")
                
                for msg in messages:
                    role_emoji = "👤" if msg.role == MessageRole.USER else "🤖"
                    f.write(f"## {role_emoji} {msg.role.value.title()}\n\n")
                    f.write(f"{msg.content}\n\n")
                    if include_metadata and msg.message_metadata:
                        f.write(f"*Metadata: {json.dumps(msg.message_metadata)}*\n\n")
                    f.write("---\n\n")
        elif format == "txt":
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Conversation: {conversation.title}\n")
                f.write(f"Created: {conversation.created_at}\n")
                f.write(f"Assistant: {conversation.assistant_id}\n\n")
                f.write("=" * 50 + "\n\n")
                
                for msg in messages:
                    f.write(f"[{msg.role.value.upper()}]\n")
                    f.write(f"{msg.content}\n\n")
        else:
            return None
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Generate download URL (expires in 24 hours)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        download_url = f"/api/v1/conversations/{conversation_id}/export/download/{filename}"
        
        return {
            "download_url": download_url,
            "filename": filename,
            "size": file_size,
            "expires_at": expires_at.isoformat()
        }
    
    def get_conversation_context(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation context.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Optional[Dict[str, Any]]: Context data
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            return None
        
        # Get context from conversation metadata
        context = conversation.conversation_metadata.get("context", {}) if conversation.conversation_metadata else {}
        
        return {
            "conversation_id": conversation_id,
            "context_window": context.get("context_window", 50),
            "relevant_documents": context.get("relevant_documents", []),
            "assistant_context": context.get("assistant_context", {}),
            "user_preferences": context.get("user_preferences", {})
        }
    
    def update_conversation_context(
        self,
        conversation_id: str,
        context_update: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update conversation context.
        
        Args:
            conversation_id: Conversation ID
            context_update: Context data to update
            
        Returns:
            Optional[Dict[str, Any]]: Updated context data
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            return None
        
        # Initialize metadata if not exists
        if not conversation.conversation_metadata:
            conversation.conversation_metadata = {}
        
        # Initialize context if not exists
        if "context" not in conversation.conversation_metadata:
            conversation.conversation_metadata["context"] = {}
        
        # Update context
        conversation.conversation_metadata["context"].update(context_update)
        conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(conversation)
        
        return self.get_conversation_context(conversation_id)
    
    def switch_assistant(
        self,
        conversation_id: str,
        new_assistant_id: str,
        preserve_context: bool = True,
        user_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Switch the active assistant for a conversation.
        
        Args:
            conversation_id: Conversation ID
            new_assistant_id: New assistant ID
            preserve_context: Whether to preserve conversation context
            user_id: User ID for verification
            
        Returns:
            Optional[Dict[str, Any]]: Switch result
        """
        # Verify conversation access
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            return None
        
        # Store old assistant ID
        old_assistant_id = conversation.assistant_id
        
        # Update assistant
        conversation.assistant_id = new_assistant_id
        conversation.updated_at = datetime.utcnow()
        
        # Update metadata
        if not conversation.conversation_metadata:
            conversation.conversation_metadata = {}
        
        conversation.conversation_metadata["assistant_switch"] = {
            "old_assistant_id": old_assistant_id,
            "new_assistant_id": new_assistant_id,
            "switched_at": datetime.utcnow().isoformat(),
            "preserve_context": preserve_context
        }
        
        # If not preserving context, clear conversation history
        if not preserve_context:
            # Delete all messages except the first system message
            self.db.query(Message).filter(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.role != MessageRole.SYSTEM
                )
            ).delete()
            
            conversation.message_count = 0
            conversation.total_tokens = 0
        
        self.db.commit()
        self.db.refresh(conversation)
        
        # TODO: Get assistant details from assistant service
        assistant_name = f"Assistant {new_assistant_id}"
        
        return {
            "assistant_name": assistant_name,
            "old_assistant_id": old_assistant_id,
            "new_assistant_id": new_assistant_id,
            "context_preserved": preserve_context
        }
    
    def get_conversation_assistant(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current assistant for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Optional[Dict[str, Any]]: Assistant data
        """
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            return None
        
        # TODO: Get assistant details from assistant service
        return {
            "id": conversation.assistant_id,
            "name": f"Assistant {conversation.assistant_id}",
            "description": "AI Assistant",
            "avatar": "",
            "capabilities": ["chat", "rag", "tools"]
        }
    
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
        
        conversation.is_active = False
        conversation.archived_at = datetime.utcnow()
        self.db.commit()
        
        return True 