"""Conversation service for managing chat conversations."""

from typing import List, Optional
from sqlalchemy.orm import Session


class ConversationService:
    """Service for managing conversations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_conversations(self, user_id: str) -> List:
        """Get conversations for a user."""
        return []
    
    def create_conversation(self, user_id: str, assistant_id: str, title: str = "") -> Optional[dict]:
        """Create a new conversation."""
        return {"message": "Conversation service - to be implemented"} 