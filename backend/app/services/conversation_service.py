"""Conversation service for managing chat conversations."""

from typing import Any

from app.core.database import get_db
from app.core.exceptions import (
    ConversationError,
    DatabaseError,
    NotFoundError,
    ValidationError,
)
from app.models.conversation import Conversation, Message, MessageRole
from app.schemas.conversation import (
    ConversationCreate,
    MessageCreate,
)
from sqlalchemy import and_, desc
from sqlalchemy.orm import joinedload


class ConversationService:
    """Service for managing conversations."""

    def __init__(self, db=None):
        self.db = db or get_db()

    def create_conversation(
        self,
        conversation_data: ConversationCreate,
    ) -> dict[str, Any]:
        """
        Create a new conversation with validation.

        Args:
            conversation_data: Conversation creation data

        Returns:
            Dict[str, Any]: Created conversation data

        Raises:
            ValidationError: If conversation data is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate conversation data
            if not conversation_data.title or not conversation_data.title.strip():
                raise ValidationError("title", "Conversation title is required")

            # Create conversation
            conversation = Conversation(
                user_id=str(conversation_data.user_id),
                assistant_id=str(conversation_data.assistant_id),
                title=conversation_data.title.strip(),
                description=conversation_data.description,
                conversation_metadata=conversation_data.conversation_metadata,
                is_active=True,
            )

            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

            return conversation.to_dict()

        except Exception as e:
            self.db.rollback()
            if isinstance(e, ValidationError | ConversationError):
                raise
            raise DatabaseError(
                f"Failed to create conversation: {str(e)}",
                operation="create_conversation",
            )

    def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        """
        Get conversation by ID and verify ownership.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for verification

        Returns:
            Dict[str, Any]: Conversation data

        Raises:
            ValidationError: If conversation_id is invalid
            NotFoundError: If conversation not found or not owned
            DatabaseError: If database operation fails
        """
        try:
            # Validate inputs
            if not conversation_id or not conversation_id.strip():
                raise ValidationError("conversation_id", "Conversation ID is required")

            if not user_id or not user_id.strip():
                raise ValidationError("user_id", "User ID is required")

            conversation = (
                self.db.query(Conversation)
                .filter(
                    and_(
                        Conversation.id == conversation_id.strip(),
                        Conversation.user_id == user_id.strip(),
                    ),
                )
                .first()
            )

            if not conversation:
                raise NotFoundError("Conversation", conversation_id)

            return conversation.to_dict()

        except Exception as e:
            if isinstance(e, ValidationError | NotFoundError):
                raise
            raise DatabaseError(
                f"Failed to get conversation: {str(e)}",
                operation="get_conversation",
            )

    def get_user_conversations(self, user_id: str) -> list[dict[str, Any]]:
        """
        Get all conversations for a user.

        Args:
            user_id: User ID

        Returns:
            List[Dict[str, Any]]: List of conversations
        """
        conversations = (
            self.db.query(Conversation)
            .options(joinedload(Conversation.assistant))  # Load assistant relationship
            .filter(
                Conversation.user_id == user_id,
            )
            .order_by(desc(Conversation.updated_at))
            .all()
        )

        return [conv.to_dict() for conv in conversations]

    def add_message(
        self,
        message_data: MessageCreate,
    ) -> dict[str, Any]:
        """
        Add a message to a conversation with validation.

        Args:
            message_data: Message creation data

        Returns:
            Dict[str, Any]: Created message data

        Raises:
            ValidationError: If message data is invalid
            NotFoundError: If conversation not found
            DatabaseError: If database operation fails
        """
        try:
            # Validate message data
            if not message_data.content or not message_data.content.strip():
                raise ValidationError("content", "Message content is required")

            # Check if conversation exists
            conversation = (
                self.db.query(Conversation)
                .filter(Conversation.id == message_data.conversation_id)
                .first()
            )

            if not conversation:
                raise NotFoundError("Conversation", str(message_data.conversation_id))

            # Create message
            message = Message(
                conversation_id=str(message_data.conversation_id),
                content=message_data.content.strip(),
                role=message_data.role,
                message_type=message_data.message_type,
                tool_name=message_data.tool_name,
                tool_input=message_data.tool_input,
                tool_output=message_data.tool_output,
                tokens_used=message_data.tokens_used or 0,
                model_used=message_data.model_used,
                message_metadata=message_data.message_metadata or {},
            )

            self.db.add(message)

            # Update conversation statistics
            conversation.message_count += 1
            if message.tokens_used:
                conversation.total_tokens += message.tokens_used

            self.db.commit()
            self.db.refresh(message)

            return message.to_dict()

        except Exception as e:
            self.db.rollback()
            if isinstance(e, ValidationError | NotFoundError):
                raise
            raise DatabaseError(
                f"Failed to add message: {str(e)}",
                operation="add_message",
            )

    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get messages in a conversation with pagination.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List[Dict[str, Any]]: List of messages

        Raises:
            ValidationError: If conversation_id is invalid
            NotFoundError: If conversation not found
            DatabaseError: If database operation fails
        """
        try:
            # Validate inputs
            if not conversation_id or not conversation_id.strip():
                raise ValidationError("conversation_id", "Conversation ID is required")

            # Check if conversation exists
            conversation = (
                self.db.query(Conversation)
                .filter(Conversation.id == conversation_id.strip())
                .first()
            )

            if not conversation:
                raise NotFoundError("Conversation", conversation_id)

            # Build query
            query = (
                self.db.query(Message)
                .filter(Message.conversation_id == conversation_id.strip())
                .order_by(Message.created_at)
            )

            # Apply pagination
            if offset is not None:
                if offset < 0:
                    raise ValidationError("offset", "Offset cannot be negative")
                query = query.offset(offset)

            if limit is not None:
                if limit < 1 or limit > 1000:
                    raise ValidationError("limit", "Limit must be between 1 and 1000")
                query = query.limit(limit)

            messages = query.all()
            return [msg.to_dict() for msg in messages]

        except Exception as e:
            if isinstance(e, ValidationError | NotFoundError):
                raise
            raise DatabaseError(
                f"Failed to get conversation messages: {str(e)}",
                operation="get_conversation_messages",
            )

    def get_conversation_history(self, conversation_id: str) -> list[dict[str, str]]:
        """
        Get conversation history for AI context.

        Args:
            conversation_id: Conversation ID

        Returns:
            List[Dict[str, str]]: List of messages in LiteLLM format
        """
        messages = (
            self.db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
            )
            .order_by(Message.created_at)
            .all()
        )

        # Convert to LiteLLM format
        history = []
        for msg in messages:
            if msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                history.append(
                    {
                        "role": msg.role.value,
                        "content": msg.content,
                    },
                )

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
        conversation = (
            self.db.query(Conversation)
            .filter(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                ),
            )
            .first()
        )

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
        conversation = (
            self.db.query(Conversation)
            .filter(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                ),
            )
            .first()
        )

        if not conversation:
            return False

        conversation.is_archived = True
        conversation.is_active = False
        self.db.commit()

        return True


# Global conversation service instance (for static access, e.g. in AIService)
from app.core.database import get_db
conversation_service = ConversationService(next(get_db()))
