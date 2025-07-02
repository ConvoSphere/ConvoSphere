"""Tool service for managing available tools."""

from typing import List, Optional
from sqlalchemy.orm import Session


class ToolService:
    """Service for managing tools."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_available_tools(self) -> List:
        """Get all available tools."""
        return []
    
    def get_tool_by_id(self, tool_id: str) -> Optional[dict]:
        """Get tool by ID."""
        return {"message": "Tool service - to be implemented"} 