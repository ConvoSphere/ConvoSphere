"""
Assistant service for managing AI assistants.

This module provides business logic for creating, updating, and managing
AI assistants with their personality profiles and tool configurations.
"""

from typing import Any

from loguru import logger
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.assistant import Assistant, AssistantStatus


class AssistantService:
    """Service for managing AI assistants."""

    def __init__(self, db: Session):
        self.db = db

    def create_assistant(
        self,
        user_id: str,
        name: str,
        system_prompt: str,
        description: str | None = None,
        personality: str | None = None,
        instructions: str | None = None,
        model: str = "gpt-4",
        temperature: str = "0.7",
        max_tokens: str = "4096",
        category: str | None = None,
        tags: list[str] | None = None,
        is_public: bool = False,
        is_template: bool = False,
    ) -> Assistant:
        """
        Create a new assistant.

        Args:
            user_id: ID of the user creating the assistant
            name: Assistant name
            system_prompt: System prompt for the assistant
            description: Assistant description
            personality: Personality profile
            instructions: Additional instructions
            model: AI model to use
            temperature: Model temperature
            max_tokens: Maximum tokens
            category: Assistant category
            tags: List of tags
            is_public: Whether assistant is public
            is_template: Whether assistant is a template

        Returns:
            Assistant: Created assistant

        Raises:
            ValueError: If required fields are missing
        """
        if not name or not system_prompt:
            raise ValueError("Name and system_prompt are required")

        assistant = Assistant(
            creator_id=user_id,
            name=name,
            description=description,
            personality=personality,
            system_prompt=system_prompt,
            instructions=instructions,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            category=category,
            tags=tags or [],
            is_public=is_public,
            is_template=is_template,
            status=AssistantStatus.DRAFT,
        )

        self.db.add(assistant)
        self.db.commit()
        self.db.refresh(assistant)

        logger.info(f"Assistant created: {assistant.name} by user {user_id}")
        return assistant

    def get_assistant(self, assistant_id: str) -> Assistant | None:
        """
        Get assistant by ID.

        Args:
            assistant_id: Assistant ID

        Returns:
            Optional[Assistant]: Assistant if found, None otherwise
        """
        return self.db.query(Assistant).filter(Assistant.id == assistant_id).first()

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

    def update_assistant(
        self,
        assistant_id: str,
        user_id: str,
        **kwargs,
    ) -> Assistant | None:
        """
        Update an assistant.

        Args:
            assistant_id: Assistant ID
            user_id: User ID (for authorization)
            **kwargs: Fields to update

        Returns:
            Optional[Assistant]: Updated assistant if found and authorized
        """
        assistant = self.get_assistant(assistant_id)

        if not assistant:
            return None

        if assistant.creator_id != user_id:
            logger.warning(
                f"Unauthorized update attempt: user {user_id} tried to update assistant {assistant_id}",
            )
            return None

        # Update fields
        for field, value in kwargs.items():
            if hasattr(assistant, field):
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
        assistant = self.get_assistant(assistant_id)

        if not assistant:
            return False

        if assistant.creator_id != user_id:
            logger.warning(
                f"Unauthorized delete attempt: user {user_id} tried to delete assistant {assistant_id}",
            )
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
        return self.update_assistant(
            assistant_id,
            user_id,
            status=AssistantStatus.ACTIVE,
        )

    def deactivate_assistant(self, assistant_id: str, user_id: str) -> Assistant | None:
        """
        Deactivate an assistant.

        Args:
            assistant_id: Assistant ID
            user_id: User ID (for authorization)

        Returns:
            Optional[Assistant]: Deactivated assistant
        """
        return self.update_assistant(
            assistant_id,
            user_id,
            status=AssistantStatus.INACTIVE,
        )

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
        assistant = self.get_assistant(assistant_id)

        if not assistant or assistant.creator_id != user_id:
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
        assistant = self.get_assistant(assistant_id)

        if not assistant or assistant.creator_id != user_id:
            return None

        if assistant.remove_tool(tool_id):
            self.db.commit()
            self.db.refresh(assistant)
            logger.info(f"Tool {tool_id} removed from assistant {assistant.name}")
            return assistant

        return None
