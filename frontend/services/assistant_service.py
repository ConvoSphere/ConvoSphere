"""
Assistant service for the AI Assistant Platform.

This module provides assistant management functionality including
CRUD operations, tool assignment, and status management.
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from .api import api_client
from .error_handler import handle_api_error, handle_network_error
from utils.helpers import generate_id, format_timestamp


@dataclass
class Assistant:
    """Assistant data model."""
    id: str
    name: str
    description: str
    model: str
    status: str
    temperature: float
    max_tokens: int
    tools: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None


class AssistantService:
    """Service for managing assistants."""
    
    def __init__(self):
        """Initialize the assistant service."""
        self.assistants: List[Assistant] = []
        self.is_loading = False
        self.current_assistant: Optional[Assistant] = None
    
    async def get_assistants(self, force_refresh: bool = False) -> List[Assistant]:
        """
        Get all assistants.
        
        Args:
            force_refresh: Force refresh from API
            
        Returns:
            List of assistants
        """
        if not force_refresh and self.assistants:
            return self.assistants
        
        self.is_loading = True
        
        try:
            response = await api_client.get_assistants()
            
            if response.success and response.data:
                self.assistants = []
                for assistant_data in response.data:
                    assistant = self._create_assistant_from_data(assistant_data)
                    self.assistants.append(assistant)
                
                return self.assistants
            else:
                handle_api_error(response, "Laden der Assistenten")
                return []
                
        except Exception as e:
            handle_network_error(e, "Laden der Assistenten")
            return []
        finally:
            self.is_loading = False
    
    async def get_assistant(self, assistant_id: str) -> Optional[Assistant]:
        """
        Get specific assistant by ID.
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            Assistant or None if not found
        """
        try:
            response = await api_client.get_assistant(assistant_id)
            
            if response.success and response.data:
                assistant = self._create_assistant_from_data(response.data)
                self.current_assistant = assistant
                return assistant
            else:
                handle_api_error(response, f"Laden des Assistenten {assistant_id}")
                return None
                
        except Exception as e:
            handle_network_error(e, f"Laden des Assistenten {assistant_id}")
            return None
    
    async def create_assistant(self, assistant_data: Dict[str, Any]) -> Optional[Assistant]:
        """
        Create new assistant.
        
        Args:
            assistant_data: Assistant data
            
        Returns:
            Created assistant or None if failed
        """
        try:
            # Validate required fields
            if not assistant_data.get("name"):
                raise ValueError("Assistenten-Name ist erforderlich")
            
            if not assistant_data.get("description"):
                raise ValueError("Assistenten-Beschreibung ist erforderlich")
            
            # Set defaults
            assistant_data.setdefault("model", "gpt-4")
            assistant_data.setdefault("temperature", 0.7)
            assistant_data.setdefault("max_tokens", 4096)
            assistant_data.setdefault("tools", [])
            assistant_data.setdefault("status", "active")
            
            response = await api_client.create_assistant(assistant_data)
            
            if response.success and response.data:
                assistant = self._create_assistant_from_data(response.data)
                self.assistants.append(assistant)
                return assistant
            else:
                handle_api_error(response, "Erstellen des Assistenten")
                return None
                
        except Exception as e:
            handle_network_error(e, "Erstellen des Assistenten")
            return None
    
    async def update_assistant(self, assistant_id: str, assistant_data: Dict[str, Any]) -> Optional[Assistant]:
        """
        Update assistant.
        
        Args:
            assistant_id: Assistant ID
            assistant_data: Updated assistant data
            
        Returns:
            Updated assistant or None if failed
        """
        try:
            response = await api_client.update_assistant(assistant_id, assistant_data)
            
            if response.success and response.data:
                assistant = self._create_assistant_from_data(response.data)
                
                # Update in local list
                for i, existing_assistant in enumerate(self.assistants):
                    if existing_assistant.id == assistant_id:
                        self.assistants[i] = assistant
                        break
                
                # Update current assistant if it's the same
                if self.current_assistant and self.current_assistant.id == assistant_id:
                    self.current_assistant = assistant
                
                return assistant
            else:
                handle_api_error(response, f"Aktualisieren des Assistenten {assistant_id}")
                return None
                
        except Exception as e:
            handle_network_error(e, f"Aktualisieren des Assistenten {assistant_id}")
            return None
    
    async def delete_assistant(self, assistant_id: str) -> bool:
        """
        Delete assistant.
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await api_client.delete_assistant(assistant_id)
            
            if response.success:
                # Remove from local list
                self.assistants = [a for a in self.assistants if a.id != assistant_id]
                
                # Clear current assistant if it's the same
                if self.current_assistant and self.current_assistant.id == assistant_id:
                    self.current_assistant = None
                
                return True
            else:
                handle_api_error(response, f"Löschen des Assistenten {assistant_id}")
                return False
                
        except Exception as e:
            handle_network_error(e, f"Löschen des Assistenten {assistant_id}")
            return False
    
    async def activate_assistant(self, assistant_id: str) -> bool:
        """
        Activate assistant.
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            True if successful, False otherwise
        """
        return await self.update_assistant(assistant_id, {"status": "active"}) is not None
    
    async def deactivate_assistant(self, assistant_id: str) -> bool:
        """
        Deactivate assistant.
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            True if successful, False otherwise
        """
        return await self.update_assistant(assistant_id, {"status": "inactive"}) is not None
    
    async def assign_tools(self, assistant_id: str, tool_ids: List[str]) -> bool:
        """
        Assign tools to assistant.
        
        Args:
            assistant_id: Assistant ID
            tool_ids: List of tool IDs
            
        Returns:
            True if successful, False otherwise
        """
        return await self.update_assistant(assistant_id, {"tools": tool_ids}) is not None
    
    def get_active_assistants(self) -> List[Assistant]:
        """
        Get only active assistants.
        
        Returns:
            List of active assistants
        """
        return [a for a in self.assistants if a.status == "active"]
    
    def search_assistants(self, query: str) -> List[Assistant]:
        """
        Search assistants by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching assistants
        """
        query_lower = query.lower()
        return [
            a for a in self.assistants
            if query_lower in a.name.lower() or query_lower in a.description.lower()
        ]
    
    def get_assistant_by_name(self, name: str) -> Optional[Assistant]:
        """
        Get assistant by name.
        
        Args:
            name: Assistant name
            
        Returns:
            Assistant or None if not found
        """
        for assistant in self.assistants:
            if assistant.name.lower() == name.lower():
                return assistant
        return None
    
    def _create_assistant_from_data(self, data: Dict[str, Any]) -> Assistant:
        """
        Create Assistant object from API data.
        
        Args:
            data: API response data
            
        Returns:
            Assistant object
        """
        return Assistant(
            id=data.get("id", generate_id("assistant_")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            model=data.get("model", "gpt-4"),
            status=data.get("status", "active"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 4096),
            tools=data.get("tools", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            created_by=data.get("created_by")
        )
    
    def get_assistant_stats(self) -> Dict[str, Any]:
        """
        Get assistant statistics.
        
        Returns:
            Dictionary with statistics
        """
        total = len(self.assistants)
        active = len(self.get_active_assistants())
        
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "models": list(set(a.model for a in self.assistants))
        }


# Global assistant service instance
assistant_service = AssistantService() 