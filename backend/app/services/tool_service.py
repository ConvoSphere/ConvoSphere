"""Tool service for managing available tools."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from loguru import logger
import uuid

from app.models.tool import Tool, ToolCategory
from app.models.user import User


class ToolService:
    """Service for managing tools."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_available_tools(self, user_id: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all available tools with optional filtering.
        
        Args:
            user_id: User ID for permission checking
            category: Filter by tool category
            
        Returns:
            List[Dict[str, Any]]: List of available tools
        """
        try:
            query = self.db.query(Tool).filter(Tool.is_enabled == True)
            
            # Filter by category if specified
            if category:
                try:
                    tool_category = ToolCategory(category)
                    query = query.filter(Tool.category == tool_category)
                except ValueError:
                    logger.warning(f"Invalid tool category: {category}")
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
            
        except Exception as e:
            logger.error(f"Error getting available tools: {e}")
            return []
    
    def get_tool_by_id(self, tool_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
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
            
        except Exception as e:
            logger.error(f"Error getting tool by ID {tool_id}: {e}")
            return None
    
    def create_tool(self, tool_data: Dict[str, Any], creator_id: str) -> Optional[Dict[str, Any]]:
        """
        Create a new tool.
        
        Args:
            tool_data: Tool data
            creator_id: ID of the user creating the tool
            
        Returns:
            Optional[Dict[str, Any]]: Created tool information or None if failed
        """
        try:
            # Validate required fields
            required_fields = ["name", "category", "function_name"]
            for field in required_fields:
                if field not in tool_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate category
            try:
                category = ToolCategory(tool_data["category"])
            except ValueError:
                raise ValueError(f"Invalid tool category: {tool_data['category']}")
            
            # Check if function_name already exists
            existing_tool = self.db.query(Tool).filter(
                Tool.function_name == tool_data["function_name"]
            ).first()
            
            if existing_tool:
                raise ValueError(f"Tool with function name '{tool_data['function_name']}' already exists")
            
            # Create new tool
            new_tool = Tool(
                name=tool_data["name"],
                description=tool_data.get("description"),
                version=tool_data.get("version", "1.0.0"),
                category=category,
                function_name=tool_data["function_name"],
                parameters_schema=tool_data.get("parameters_schema"),
                implementation_path=tool_data.get("implementation_path"),
                is_builtin=tool_data.get("is_builtin", False),
                is_enabled=tool_data.get("is_enabled", True),
                requires_auth=tool_data.get("requires_auth", False),
                required_permissions=tool_data.get("required_permissions", []),
                rate_limit=tool_data.get("rate_limit"),
                tags=tool_data.get("tags", []),
                tool_metadata=tool_data.get("tool_metadata", {}),
                creator_id=creator_id
            )
            
            self.db.add(new_tool)
            self.db.commit()
            self.db.refresh(new_tool)
            
            logger.info(f"Created new tool: {new_tool.name} by user {creator_id}")
            return new_tool.to_dict()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating tool: {e}")
            return None
    
    def update_tool(self, tool_id: str, tool_data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
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
            # Get existing tool
            tool = self.db.query(Tool).filter(Tool.id == tool_id).first()
            
            if not tool:
                logger.warning(f"Tool not found for update: {tool_id}")
                return None
            
            # Check if user has permission to update this tool
            if not self._can_edit_tool(tool, user_id):
                logger.warning(f"User {user_id} does not have permission to edit tool {tool_id}")
                return None
            
            # Update fields
            if "name" in tool_data:
                tool.name = tool_data["name"]
            
            if "description" in tool_data:
                tool.description = tool_data["description"]
            
            if "version" in tool_data:
                tool.version = tool_data["version"]
            
            if "category" in tool_data:
                try:
                    tool.category = ToolCategory(tool_data["category"])
                except ValueError:
                    raise ValueError(f"Invalid tool category: {tool_data['category']}")
            
            if "parameters_schema" in tool_data:
                tool.parameters_schema = tool_data["parameters_schema"]
            
            if "implementation_path" in tool_data:
                tool.implementation_path = tool_data["implementation_path"]
            
            if "is_enabled" in tool_data:
                tool.is_enabled = tool_data["is_enabled"]
            
            if "requires_auth" in tool_data:
                tool.requires_auth = tool_data["requires_auth"]
            
            if "required_permissions" in tool_data:
                tool.required_permissions = tool_data["required_permissions"]
            
            if "rate_limit" in tool_data:
                tool.rate_limit = tool_data["rate_limit"]
            
            if "tags" in tool_data:
                tool.tags = tool_data["tags"]
            
            if "tool_metadata" in tool_data:
                tool.tool_metadata = tool_data["tool_metadata"]
            
            self.db.commit()
            self.db.refresh(tool)
            
            logger.info(f"Updated tool: {tool.name} by user {user_id}")
            return tool.to_dict()
            
        except Exception as e:
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
            # Get tool
            tool = self.db.query(Tool).filter(Tool.id == tool_id).first()
            
            if not tool:
                logger.warning(f"Tool not found for deletion: {tool_id}")
                return False
            
            # Check if user has permission to delete this tool
            if not self._can_edit_tool(tool, user_id):
                logger.warning(f"User {user_id} does not have permission to delete tool {tool_id}")
                return False
            
            # Check if tool is builtin (builtin tools cannot be deleted)
            if tool.is_builtin:
                logger.warning(f"Cannot delete builtin tool: {tool_id}")
                return False
            
            # Delete tool
            self.db.delete(tool)
            self.db.commit()
            
            logger.info(f"Deleted tool: {tool.name} by user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting tool {tool_id}: {e}")
            return False
    
    def get_tools_by_category(self, category: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get tools by category.
        
        Args:
            category: Tool category
            user_id: User ID for permission checking
            
        Returns:
            List[Dict[str, Any]]: List of tools in the category
        """
        try:
            tool_category = ToolCategory(category)
            return self.get_available_tools(user_id=user_id, category=category)
            
        except ValueError:
            logger.warning(f"Invalid tool category: {category}")
            return []
    
    def search_tools(self, query: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
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
            tools = self.db.query(Tool).filter(
                and_(
                    Tool.is_enabled == True,
                    (Tool.name.ilike(f"%{query}%") | Tool.description.ilike(f"%{query}%"))
                )
            ).all()
            
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
            
            logger.info(f"Found {len(result)} tools matching query: {query}")
            return result
            
        except Exception as e:
            logger.error(f"Error searching tools: {e}")
            return []
    
    def _check_user_permission(self, tool: Tool, user_id: str) -> bool:
        """
        Check if user has permission to use a tool.
        
        Args:
            tool: Tool to check
            user_id: User ID
            
        Returns:
            bool: True if user has permission
        """
        try:
            # If tool doesn't require auth, anyone can use it
            if not tool.requires_auth:
                return True
            
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return False
            
            # Check if user has required permissions
            if tool.required_permissions:
                for permission in tool.required_permissions:
                    if not user.has_permission(permission):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking user permission for tool: {e}")
            return False
    
    def _can_edit_tool(self, tool: Tool, user_id: str) -> bool:
        """
        Check if user can edit a tool.
        
        Args:
            tool: Tool to check
            user_id: User ID
            
        Returns:
            bool: True if user can edit
        """
        try:
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return False
            
            # Admin can edit any tool
            if user.role.value == "admin":
                return True
            
            # Creator can edit their own tools
            if tool.creator_id == user_id:
                return True
            
            # Manager can edit non-builtin tools
            if user.role.value == "manager" and not tool.is_builtin:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking edit permission for tool: {e}")
            return False

    def execute_tool(self, tool_name: str, user_id: str, **kwargs) -> Any:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            user_id: User ID for execution context
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            # Get tool by function name
            tool = self.db.query(Tool).filter(
                and_(
                    Tool.function_name == tool_name,
                    Tool.is_enabled == True
                )
            ).first()
            
            if not tool:
                raise ValueError(f"Tool '{tool_name}' not found or disabled")
            
            # Check if user has permission to use this tool
            if not self._check_user_permission(tool, user_id):
                raise PermissionError(f"User {user_id} does not have permission to use tool '{tool_name}'")
            
            # Import and execute tool function
            if tool.implementation_path:
                try:
                    # Dynamic import of tool implementation
                    module_path, function_name = tool.implementation_path.rsplit('.', 1)
                    module = __import__(module_path, fromlist=[function_name])
                    tool_function = getattr(module, function_name)
                    
                    # Execute tool with parameters
                    result = tool_function(user_id=user_id, **kwargs)
                    return result
                    
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    raise RuntimeError(f"Tool execution failed: {str(e)}")
            else:
                # Built-in tool execution
                return self._execute_builtin_tool(tool_name, user_id, **kwargs)
                
        except Exception as e:
            logger.error(f"Error in tool execution: {e}")
            raise
    
    def get_tools_for_assistant(self, assistant_id: str) -> List[Dict[str, Any]]:
        """
        Get tools available for an assistant.
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            List[Dict[str, Any]]: List of tools available for the assistant
        """
        try:
            # For now, return all available tools
            # In the future, this could be filtered based on assistant configuration
            tools = self.get_available_tools()
            
            # Convert to tool definitions for AI
            tool_definitions = []
            for tool in tools:
                if tool.get("can_use", True):
                    tool_def = {
                        "name": tool.get("function_name"),
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters_schema", {}),
                        "category": tool.get("category"),
                        "status": "active" if tool.get("is_enabled") else "inactive"
                    }
                    tool_definitions.append(tool_def)
            
            return tool_definitions
            
        except Exception as e:
            logger.error(f"Error getting tools for assistant {assistant_id}: {e}")
            return []
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all available tools.
        
        Returns:
            List[Dict[str, Any]]: List of all available tools
        """
        try:
            return self.get_available_tools()
        except Exception as e:
            logger.error(f"Error getting all tools: {e}")
            return []
    
    def _execute_builtin_tool(self, tool_name: str, user_id: str, **kwargs) -> Any:
        """
        Execute a built-in tool.
        
        Args:
            tool_name: Name of the built-in tool
            user_id: User ID for execution context
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            # Import built-in tools
            from app.tools.search_tools import search_web, search_wikipedia
            from app.tools.file_tools import read_file, write_file
            from app.tools.analysis_tools import analyze_text, summarize_text
            
            # Map tool names to functions
            builtin_tools = {
                "search_web": search_web,
                "search_wikipedia": search_wikipedia,
                "read_file": read_file,
                "write_file": write_file,
                "analyze_text": analyze_text,
                "summarize_text": summarize_text
            }
            
            if tool_name not in builtin_tools:
                raise ValueError(f"Built-in tool '{tool_name}' not found")
            
            # Execute tool
            tool_function = builtin_tools[tool_name]
            result = tool_function(user_id=user_id, **kwargs)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing built-in tool {tool_name}: {e}")
            raise RuntimeError(f"Built-in tool execution failed: {str(e)}")


# Global tool service instance (for static access, e.g. in AIService)
tool_service = None  # Must be initialized with DB-Session, e.g. in FastAPI startup or via Dependency Injection 