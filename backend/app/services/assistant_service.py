"""
Assistant service for managing AI assistants.

This module provides business logic for creating, updating, and managing
AI assistants with their personality profiles and tool configurations.
"""

from typing import Any

from app.core.database import get_db
from app.models.assistant import Assistant, AssistantStatus
from loguru import logger
from sqlalchemy import and_, or_


class AssistantService:
    """Service for managing AI assistants."""

    def __init__(self, db=None):
        self.db = db or get_db()

    def create_assistant(
        self,
        assistant_data: Any,  # Accepts AssistantCreate
        user_id: str,
    ) -> Assistant:
        """
        Create a new assistant.
        """
        # Use attribute access for Pydantic models
        if not getattr(assistant_data, 'name', None) or not getattr(assistant_data, 'system_prompt', None):
            raise ValueError("Name and system_prompt are required")

        assistant = Assistant(
            creator_id=user_id,
            name=assistant_data.name,
            description=getattr(assistant_data, 'description', None),
            personality=getattr(assistant_data, 'personality', None),
            system_prompt=assistant_data.system_prompt,
            instructions=getattr(assistant_data, 'instructions', None),
            model=getattr(assistant_data, 'model', 'gpt-4'),
            temperature=str(getattr(assistant_data, 'temperature', 0.7)),
            max_tokens=str(getattr(assistant_data, 'max_tokens', 4096)),
            category=getattr(assistant_data, 'category', None),
            tags=getattr(assistant_data, 'tags', []),
            is_public=getattr(assistant_data, 'is_public', False),
            is_template=getattr(assistant_data, 'is_template', False),
            status=AssistantStatus.DRAFT,
        )
        self.db.add(assistant)
        self.db.commit()
        self.db.refresh(assistant)
        logger.info(f"Assistant created: {assistant.name} by user {user_id}")
        return assistant

    def get_assistant(self, assistant_id: str, user_id: str | None = None) -> Assistant | None:
        """
        Get assistant by ID.

        Args:
            assistant_id: Assistant ID
            user_id: User ID for permission check (optional)

        Returns:
            Optional[Assistant]: Assistant if found, None otherwise
        """
        query = self.db.query(Assistant).filter(Assistant.id == assistant_id)
        
        # If user_id is provided, check permissions
        if user_id:
            query = query.filter(
                or_(
                    Assistant.creator_id == user_id,
                    Assistant.is_public == True
                )
            )
        
        return query.first()

    def get_user_assistants(
        self,
        user_id: str,
        include_public: bool = True,
        status: AssistantStatus | None = None,
    ) -> list[Assistant]:
        """
        Get assistants for a user.

        Args:
            user_id: User ID
            include_public: Whether to include public assistants
            status: Filter by status

        Returns:
            List[Assistant]: List of assistants
        """
        query = self.db.query(Assistant)

        if include_public:
            query = query.filter(
                or_(
                    Assistant.creator_id == user_id,
                    and_(
                        Assistant.is_public is True,
                        Assistant.status == AssistantStatus.ACTIVE,
                    ),
                ),
            )
        else:
            query = query.filter(Assistant.creator_id == user_id)

        if status:
            query = query.filter(Assistant.status == status)

        return query.order_by(Assistant.created_at.desc()).all()

    def get_public_assistants(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
        limit: int = 50,
    ) -> list[Assistant]:
        """
        Get public assistants.

        Args:
            category: Filter by category
            tags: Filter by tags
            limit: Maximum number of results

        Returns:
            List[Assistant]: List of public assistants
        """
        query = self.db.query(Assistant).filter(
            and_(
                Assistant.is_public is True,
                Assistant.status == AssistantStatus.ACTIVE,
            ),
        )

        if category:
            query = query.filter(Assistant.category == category)

        if tags:
            # Implement tag filtering
            for tag in tags:
                query = query.filter(Assistant.tags.contains([tag]))

        return query.order_by(Assistant.created_at.desc()).limit(limit).all()

    def get_default_assistant(self) -> Assistant | None:
        """
        Get the default assistant (first active public assistant).

        Returns:
            Optional[Assistant]: Default assistant if found, None otherwise
        """
        return (
            self.db.query(Assistant)
            .filter(
                and_(
                    Assistant.status == AssistantStatus.ACTIVE,
                    Assistant.is_public == True,
                ),
            )
            .first()
        )

    def get_user_default_assistant_id(self, user_id: str) -> str | None:
        """
        Get the default assistant ID for a user from their preferences.
        If no default is configured, returns the first available assistant.

        Args:
            user_id: User ID

        Returns:
            Optional[str]: Default assistant ID if configured, None otherwise
        """
        from app.models.user import User
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Check user preferences first
        if user.preferences and user.preferences.get("default_assistant_id"):
            return user.preferences.get("default_assistant_id")
        
        # Fallback: get first available assistant for user
        user_assistants = self.get_user_assistants(user_id, include_public=True)
        if user_assistants:
            return str(user_assistants[0].id)
        
        # Final fallback: get first public assistant
        public_assistants = self.get_public_assistants(limit=1)
        if public_assistants:
            return str(public_assistants[0].id)
        
        return None

    def set_user_default_assistant(self, user_id: str, assistant_id: str) -> bool:
        """
        Set the default assistant for a user.

        Args:
            user_id: User ID
            assistant_id: Assistant ID to set as default

        Returns:
            bool: True if successful, False otherwise
        """
        from app.models.user import User
        
        # Verify the assistant exists and user has access
        assistant = self.get_assistant(assistant_id, user_id)
        if not assistant:
            return False
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Initialize preferences if not exists
        if not user.preferences:
            user.preferences = {}
        
        user.preferences["default_assistant_id"] = assistant_id
        self.db.commit()
        return True

    def get_user_default_assistant(self, user_id: str) -> Assistant | None:
        """
        Get the default assistant for a user.

        Args:
            user_id: User ID

        Returns:
            Optional[Assistant]: Default assistant if configured, None otherwise
        """
        default_assistant_id = self.get_user_default_assistant_id(user_id)
        if not default_assistant_id:
            return None
        
        return self.get_assistant(default_assistant_id, user_id)

    def update_assistant(
        self,
        assistant_id: str,
        assistant_data: Any,  # Accepts AssistantUpdate
        user_id: str,
    ) -> Assistant | None:
        """
        Update an assistant.
        """
        assistant = self.get_assistant(assistant_id, user_id)
        if not assistant:
            return None
        # Update fields using attribute access
        for field in assistant_data.model_fields:
            value = getattr(assistant_data, field, None)
            if value is not None and hasattr(assistant, field):
                setattr(assistant, field, value)
        self.db.commit()
        self.db.refresh(assistant)
        logger.info(f"Assistant updated: {assistant.name} by user {user_id}")
        return assistant

    def delete_assistant(self, assistant_id: str, user_id: str) -> bool:
        """
        Delete an assistant.

        Args:
            assistant_id: Assistant ID
            user_id: User ID (for authorization)

        Returns:
            bool: True if deleted, False otherwise
        """
        assistant = self.get_assistant(assistant_id, user_id)

        if not assistant:
            return False

        self.db.delete(assistant)
        self.db.commit()

        logger.info(f"Assistant deleted: {assistant.name} by user {user_id}")
        return True

    def activate_assistant(self, assistant_id: str, user_id: str) -> Assistant | None:
        """
        Activate an assistant.

        Args:
            assistant_id: Assistant ID
            user_id: User ID (for authorization)

        Returns:
            Optional[Assistant]: Activated assistant
        """
        assistant = self.get_assistant(assistant_id, user_id)
        if not assistant:
            return None
        
        assistant.status = AssistantStatus.ACTIVE
        self.db.commit()
        self.db.refresh(assistant)
        
        logger.info(f"Assistant activated: {assistant.name} by user {user_id}")
        return assistant

    def deactivate_assistant(self, assistant_id: str, user_id: str) -> Assistant | None:
        """
        Deactivate an assistant.

        Args:
            assistant_id: Assistant ID
            user_id: User ID (for authorization)

        Returns:
            Optional[Assistant]: Deactivated assistant
        """
        assistant = self.get_assistant(assistant_id, user_id)
        if not assistant:
            return None
        
        assistant.status = AssistantStatus.INACTIVE
        self.db.commit()
        self.db.refresh(assistant)
        
        logger.info(f"Assistant deactivated: {assistant.name} by user {user_id}")
        return assistant

    def add_tool_to_assistant(
        self,
        assistant_id: str,
        user_id: str,
        tool_id: str,
        config: dict[str, Any] | None = None,
    ) -> Assistant | None:
        """
        Add a tool to an assistant.

        Args:
            assistant_id: Assistant ID
            user_id: User ID (for authorization)
            tool_id: Tool ID to add
            config: Tool configuration

        Returns:
            Optional[Assistant]: Updated assistant
        """
        assistant = self.get_assistant(assistant_id, user_id)

        if not assistant:
            return None

        assistant.add_tool(tool_id, config)
        self.db.commit()
        self.db.refresh(assistant)

        logger.info(f"Tool {tool_id} added to assistant {assistant.name}")
        return assistant

    def remove_tool_from_assistant(
        self,
        assistant_id: str,
        user_id: str,
        tool_id: str,
    ) -> Assistant | None:
        """
        Remove a tool from an assistant.

        Args:
            assistant_id: Assistant ID
            user_id: User ID (for authorization)
            tool_id: Tool ID to remove

        Returns:
            Optional[Assistant]: Updated assistant
        """
        assistant = self.get_assistant(assistant_id, user_id)

        if not assistant:
            return None

        if assistant.remove_tool(tool_id):
            self.db.commit()
            self.db.refresh(assistant)
            logger.info(f"Tool {tool_id} removed from assistant {assistant.name}")
            return assistant

        return None
