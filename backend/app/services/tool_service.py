"""Tool service for managing available tools."""

import uuid
from typing import Any
from datetime import datetime
from pytz import UTC

from loguru import logger
from sqlalchemy import and_, or_

from backend.app.core.database import get_db
from backend.app.models.tool import Tool, ToolCategory
from backend.app.models.user import User


class ToolService:
    """Service for managing tools."""

    def __init__(self, db=None):
        self.db = db or get_db()

    def get_available_tools(
        self,
        user_id: str | None = None,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get all available tools.

        Args:
            user_id: User ID for permission checking
            category: Filter by category

        Returns:
            List[Dict[str, Any]]: List of available tools
        """
        try:
            # Build query
            query = self.db.query(Tool)

            # Filter by category if specified
            if category:
                try:
                    category_enum = ToolCategory(category)
                    query = query.filter(Tool.category == category_enum)
                except ValueError:
                    logger.warning(f"Invalid category: {category}")
                    return []

            # Get tools
            tools = query.all()

            # Convert to dictionaries
            result = []
            for tool in tools:
                tool_dict = tool.to_dict()

                # Check if user has permission to use this tool
                if user_id:
                    tool_dict["can_use"] = self._check_user_permission(tool, user_id)
                else:
                    tool_dict["can_use"] = not tool.requires_auth

                result.append(tool_dict)

            logger.info(f"Retrieved {len(result)} available tools")
            return result

        except (ValueError, AttributeError) as e:
            logger.error(f"Error getting available tools: {e}")
            return []

    def get_tool_by_id(
        self,
        tool_id: str,
        user_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Get tool by ID.

        Args:
            tool_id: Tool ID
            user_id: User ID for permission checking

        Returns:
            Optional[Dict[str, Any]]: Tool information or None if not found
        """
        try:
            # Validate UUID format
            try:
                uuid.UUID(tool_id)
            except ValueError:
                logger.warning(f"Invalid tool ID format: {tool_id}")
                return None

            # Get tool from database
            tool = self.db.query(Tool).filter(Tool.id == tool_id).first()

            if not tool:
                logger.warning(f"Tool not found: {tool_id}")
                return None

            # Convert to dictionary
            tool_dict = tool.to_dict()

            # Check if user has permission to use this tool
            if user_id:
                tool_dict["can_use"] = self._check_user_permission(tool, user_id)
            else:
                tool_dict["can_use"] = not tool.requires_auth

            logger.info(f"Retrieved tool: {tool.name} ({tool_id})")
            return tool_dict

        except (ValueError, AttributeError) as e:
            logger.error(f"Error getting tool by ID {tool_id}: {e}")
            return None

    def _validate_tool_data(self, tool_data: dict[str, Any]) -> None:
        """Validate tool data and raise appropriate exceptions."""
        # Validate required fields
        required_fields = ["name", "category", "function_name"]
        for field in required_fields:
            if field not in tool_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate category
        try:
            category = ToolCategory(tool_data["category"])
        except ValueError:
            raise ValueError(f"Invalid tool category: {tool_data['category']}") from None

    def create_tool(
        self,
        tool_data: dict[str, Any],
        creator_id: str,
    ) -> dict[str, Any] | None:
        """
        Create a new tool.

        Args:
            tool_data: Tool data
            creator_id: ID of the user creating the tool

        Returns:
            Optional[Dict[str, Any]]: Created tool information or None if failed
        """
        try:
            # Validate tool data
            self._validate_tool_data(tool_data)

            # Check if function_name already exists
            existing_tool = (
                self.db.query(Tool)
                .filter(
                    Tool.function_name == tool_data["function_name"],
                )
                .first()
            )

            if existing_tool:
                raise ValueError(
                    f"Tool with function name '{tool_data['function_name']}' already exists",
                )

            # Create new tool
            new_tool = Tool(
                name=tool_data["name"],
                description=tool_data.get("description", ""),
                category=ToolCategory(tool_data["category"]),
                function_name=tool_data["function_name"],
                parameters_schema=tool_data.get("parameters_schema", {}),
                requires_auth=tool_data.get("requires_auth", False),
                is_builtin=tool_data.get("is_builtin", False),
                creator_id=creator_id,
            )

            # Add to database
            self.db.add(new_tool)
            self.db.commit()

            logger.info(f"Created tool: {new_tool.name} by user {creator_id}")
            return new_tool.to_dict()

        except (ValueError, AttributeError) as e:
            self.db.rollback()
            logger.error(f"Error creating tool: {e}")
            return None

    def update_tool(
        self,
        tool_id: str,
        tool_data: dict[str, Any],
        user_id: str,
    ) -> dict[str, Any] | None:
        """
        Update an existing tool.

        Args:
            tool_id: Tool ID
            tool_data: Updated tool data
            user_id: ID of the user updating the tool

        Returns:
            Optional[Dict[str, Any]]: Updated tool information or None if failed
        """
        try:
            # Validate UUID format
            try:
                uuid.UUID(tool_id)
            except ValueError:
                logger.warning(f"Invalid tool ID format: {tool_id}")
                return None

            # Get tool from database
            tool = self.db.query(Tool).filter(Tool.id == tool_id).first()

            if not tool:
                logger.warning(f"Tool not found: {tool_id}")
                return None

            # Check if user can edit this tool
            if not self._can_edit_tool(tool, user_id):
                logger.warning(f"User {user_id} cannot edit tool {tool_id}")
                return None

            # Update fields
            if "name" in tool_data:
                tool.name = tool_data["name"]

            if "description" in tool_data:
                tool.description = tool_data["description"]

            if "category" in tool_data:
                try:
                    tool.category = ToolCategory(tool_data["category"])
                except ValueError:
                    raise ValueError(f"Invalid tool category: {tool_data['category']}") from None

            if "parameters_schema" in tool_data:
                tool.parameters_schema = tool_data["parameters_schema"]

            if "requires_auth" in tool_data:
                tool.requires_auth = tool_data["requires_auth"]

            # Update timestamp
            tool.updated_at = datetime.now(UTC)

            # Save changes
            self.db.commit()

            logger.info(f"Updated tool: {tool.name} by user {user_id}")
            return tool.to_dict()

        except (ValueError, AttributeError) as e:
            self.db.rollback()
            logger.error(f"Error updating tool {tool_id}: {e}")
            return None

    def delete_tool(self, tool_id: str, user_id: str) -> bool:
        """
        Delete a tool.

        Args:
            tool_id: Tool ID
            user_id: ID of the user deleting the tool

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            # Validate UUID format
            try:
                uuid.UUID(tool_id)
            except ValueError:
                logger.warning(f"Invalid tool ID format: {tool_id}")
                return False

            # Get tool from database
            tool = self.db.query(Tool).filter(Tool.id == tool_id).first()

            if not tool:
                logger.warning(f"Tool not found: {tool_id}")
                return False

            # Check if user can delete this tool
            if not self._can_edit_tool(tool, user_id):
                logger.warning(f"User {user_id} cannot delete tool {tool_id}")
                return False

            # Delete tool
            self.db.delete(tool)
            self.db.commit()

            logger.info(f"Deleted tool: {tool.name} by user {user_id}")
            return True

        except (ValueError, AttributeError) as e:
            self.db.rollback()
            logger.error(f"Error deleting tool {tool_id}: {e}")
            return False

    def get_tools_by_category(
        self,
        category: str,
        user_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get tools by category.

        Args:
            category: Tool category
            user_id: User ID for permission checking

        Returns:
            List[Dict[str, Any]]: List of tools in the category
        """
        try:
            category_enum = ToolCategory(category)
            tools = self.db.query(Tool).filter(Tool.category == category_enum).all()

            result = []
            for tool in tools:
                tool_dict = tool.to_dict()

                # Check if user has permission to use this tool
                if user_id:
                    tool_dict["can_use"] = self._check_user_permission(tool, user_id)
                else:
                    tool_dict["can_use"] = not tool.requires_auth

                result.append(tool_dict)

            logger.info(f"Retrieved {len(result)} tools in category: {category}")
            return result

        except ValueError:
            logger.warning(f"Invalid category: {category}")
            return []

    def search_tools(
        self,
        query: str,
        user_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search tools by name or description.

        Args:
            query: Search query
            user_id: User ID for permission checking

        Returns:
            List[Dict[str, Any]]: List of matching tools
        """
        try:
            # Search in name and description
            tools = (
                self.db.query(Tool)
                .filter(
                    or_(
                        Tool.name.ilike(f"%{query}%"),
                        Tool.description.ilike(f"%{query}%"),
                    ),
                )
                .all()
            )

            result = []
            for tool in tools:
                tool_dict = tool.to_dict()

                # Check if user has permission to use this tool
                if user_id:
                    tool_dict["can_use"] = self._check_user_permission(tool, user_id)
                else:
                    tool_dict["can_use"] = not tool.requires_auth

                result.append(tool_dict)

            logger.info(f"Found {len(result)} tools matching query: {query}")
            return result

        except (ValueError, AttributeError) as e:
            logger.error(f"Error searching tools: {e}")
            return []

    def _check_user_permission(self, tool: Tool, user_id: str) -> bool:
        """
        Check if user has permission to use a tool.

        Args:
            tool: Tool object
            user_id: User ID

        Returns:
            bool: True if user has permission, False otherwise
        """
        try:
            # If tool doesn't require auth, anyone can use it
            if not tool.requires_auth:
                return True

            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            # Admin can use all tools
            if user.role.value == "admin":
                return True

            # Check if user has specific permission for this tool
            # The ToolPermission model is removed, so this part of the logic is no longer applicable.
            # Assuming a default permission for now, or that this logic needs to be re-evaluated
            # if specific user permissions are required.
            # For now, we'll return True if the tool doesn't require auth,
            # as the ToolPermission model is removed.
            return not tool.requires_auth

        except (ValueError, AttributeError) as e:
            logger.error(f"Error checking user permission for tool: {e}")
            return False

    def _can_edit_tool(self, tool: Tool, user_id: str) -> bool:
        """
        Check if user can edit a tool.

        Args:
            tool: Tool object
            user_id: User ID

        Returns:
            bool: True if user can edit, False otherwise
        """
        try:
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            # Admin can edit all tools
            if user.role.value == "admin":
                return True

            # Creator can edit their own tools
            if tool.creator_id == user_id:
                return True

            # Manager can edit non-builtin tools
            return bool(user.role.value == "manager" and not tool.is_builtin)
        except (ValueError, AttributeError) as e:
            logger.error(f"Error checking edit permission for tool: {e}")
            return False


# Global tool service instance (for static access, e.g. in AIService)
tool_service = None  # Muss mit DB-Session initialisiert werden, z.B. im FastAPI-Startup oder per Dependency Injection
