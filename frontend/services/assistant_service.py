"""
Assistant service for the frontend.

This module provides assistant management and state handling.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Assistant:
    """Assistant data model."""
    id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    personality: Optional[str] = None
    system_prompt: str = ""
    instructions: Optional[str] = None
    model: str = "gpt-4"
    temperature: str = "0.7"
    max_tokens: str = "4096"
    status: str = "draft"
    is_public: bool = False
    is_template: bool = False
    tools_config: List[Dict[str, Any]] = None
    tools_enabled: bool = True
    category: Optional[str] = None
    tags: List[str] = None
    creator_id: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.tools_config is None:
            self.tools_config = []
        if self.tags is None:
            self.tags = []


class AssistantService:
    """Assistant service for managing assistants."""
    
    def __init__(self):
        self.assistants: List[Assistant] = []
        self.current_assistant: Optional[Assistant] = None
    
    def set_assistants(self, assistants_data: List[Dict[str, Any]]) -> None:
        """
        Set assistants from API data.
        
        Args:
            assistants_data: List of assistant data from API
        """
        self.assistants = [
            Assistant(**assistant_data) for assistant_data in assistants_data
        ]
    
    def get_assistant_by_id(self, assistant_id: str) -> Optional[Assistant]:
        """
        Get assistant by ID.
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            Optional[Assistant]: Assistant if found
        """
        for assistant in self.assistants:
            if assistant.id == assistant_id:
                return assistant
        return None
    
    def get_active_assistants(self) -> List[Assistant]:
        """
        Get active assistants.
        
        Returns:
            List[Assistant]: List of active assistants
        """
        return [a for a in self.assistants if a.status == "active"]
    
    def get_public_assistants(self) -> List[Assistant]:
        """
        Get public assistants.
        
        Returns:
            List[Assistant]: List of public assistants
        """
        return [a for a in self.assistants if a.is_public and a.status == "active"]
    
    def get_assistants_by_category(self, category: str) -> List[Assistant]:
        """
        Get assistants by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List[Assistant]: List of assistants in category
        """
        return [a for a in self.assistants if a.category == category]
    
    def search_assistants(self, query: str) -> List[Assistant]:
        """
        Search assistants by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List[Assistant]: List of matching assistants
        """
        query_lower = query.lower()
        return [
            a for a in self.assistants
            if query_lower in a.name.lower() or 
               (a.description and query_lower in a.description.lower())
        ]
    
    def set_current_assistant(self, assistant: Assistant) -> None:
        """
        Set current assistant.
        
        Args:
            assistant: Assistant to set as current
        """
        self.current_assistant = assistant
    
    def get_current_assistant(self) -> Optional[Assistant]:
        """
        Get current assistant.
        
        Returns:
            Optional[Assistant]: Current assistant
        """
        return self.current_assistant
    
    def add_assistant(self, assistant: Assistant) -> None:
        """
        Add assistant to list.
        
        Args:
            assistant: Assistant to add
        """
        self.assistants.append(assistant)
    
    def remove_assistant(self, assistant_id: str) -> None:
        """
        Remove assistant from list.
        
        Args:
            assistant_id: Assistant ID to remove
        """
        self.assistants = [a for a in self.assistants if a.id != assistant_id]
        
        # Clear current assistant if it was removed
        if self.current_assistant and self.current_assistant.id == assistant_id:
            self.current_assistant = None
    
    def update_assistant(self, assistant_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update assistant data.
        
        Args:
            assistant_id: Assistant ID to update
            updates: Updates to apply
            
        Returns:
            bool: True if updated successfully
        """
        for assistant in self.assistants:
            if assistant.id == assistant_id:
                for key, value in updates.items():
                    if hasattr(assistant, key):
                        setattr(assistant, key, value)
                
                # Update current assistant if it was updated
                if self.current_assistant and self.current_assistant.id == assistant_id:
                    self.current_assistant = assistant
                
                return True
        
        return False


# Global assistant service instance
assistant_service = AssistantService() 